"""
Comprehensive Error Handling and Recovery System
Implements retry logic, circuit breakers, and graceful degradation
"""
from functools import wraps
from typing import Optional, Callable, Any, Type
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
import json


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisError(Exception):
    """Base exception for analysis pipeline errors"""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        self.message = message
        self.severity = severity
        super().__init__(message)


class LLMAPIError(AnalysisError):
    """LLM API call failures"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, ErrorSeverity.HIGH)
        self.status_code = status_code


class DataValidationError(AnalysisError):
    """Invalid data format or constraints"""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, ErrorSeverity.MEDIUM)
        self.field = field


class DatabaseError(AnalysisError):
    """Database operation failures"""
    def __init__(self, message: str):
        super().__init__(message, ErrorSeverity.HIGH)


class UserFacingError(Exception):
    """Errors that should be shown to users with recovery actions"""
    def __init__(
        self,
        message: str,
        recovery_action: str,
        details: Optional[str] = None,
        icon: str = "⚠️"
    ):
        self.message = message
        self.recovery_action = recovery_action
        self.details = details
        self.icon = icon
        super().__init__(message)


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance
    Prevents cascading failures by stopping calls to failing services
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        name: str = "circuit_breaker"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed = working, open = failing, half-open = testing

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            # Check if we should try again (recovery timeout elapsed)
            if (
                self.last_failure_time
                and datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
            ):
                self.state = "half-open"
                logger.info(f"Circuit breaker '{self.name}' entering half-open state")
            else:
                raise UserFacingError(
                    message="Service temporarily unavailable",
                    recovery_action="retry_later",
                    details=f"Circuit breaker '{self.name}' is open. Try again in {self.recovery_timeout}s"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        if self.state == "open":
            if (
                self.last_failure_time
                and datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
            ):
                self.state = "half-open"
                logger.info(f"Circuit breaker '{self.name}' entering half-open state")
            else:
                raise UserFacingError(
                    message="Service temporarily unavailable",
                    recovery_action="retry_later",
                    details=f"Circuit breaker '{self.name}' is open"
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Reset circuit breaker on successful call"""
        if self.state == "half-open":
            logger.info(f"Circuit breaker '{self.name}' recovered, closing")
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """Track failure and open circuit if threshold exceeded"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.error(
                f"Circuit breaker '{self.name}' opened after {self.failure_count} failures"
            )


# Global circuit breakers for services
llm_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60, name="llm_api")
db_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30, name="database")


def with_error_recovery(
    checkpoint_key: Optional[str] = None,
    max_retries: int = 3
):
    """
    Decorator for automatic error recovery and checkpointing
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # Load checkpoint if exists
                if checkpoint_key:
                    checkpoint = await load_checkpoint(checkpoint_key)
                    if checkpoint:
                        logger.info(f"Resuming from checkpoint: {checkpoint_key}")
                        kwargs['resume_from'] = checkpoint

                # Execute function with retry logic
                result = await call_with_retry_async(func, max_retries, *args, **kwargs)

                # Save checkpoint on success
                if checkpoint_key:
                    await save_checkpoint(checkpoint_key, result)

                return result

            except LLMAPIError as e:
                logger.error(f"LLM API failure: {e}", exc_info=True)
                raise UserFacingError(
                    message="AI service temporarily unavailable",
                    recovery_action="retry",
                    details=str(e),
                    icon="⏳"
                )

            except DataValidationError as e:
                logger.error(f"Data validation failure: {e}", exc_info=True)
                raise UserFacingError(
                    message="Invalid input format",
                    recovery_action="edit_input",
                    details=str(e),
                    icon="⚠️"
                )

            except DatabaseError as e:
                logger.error(f"Database error: {e}", exc_info=True)
                raise UserFacingError(
                    message="Unable to save progress",
                    recovery_action="retry_save",
                    details="Your work has been saved locally",
                    icon="💾"
                )

            except Exception as e:
                logger.critical(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                raise UserFacingError(
                    message="An unexpected error occurred",
                    recovery_action="contact_support",
                    details=str(e),
                    icon="❌"
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = call_with_retry_sync(func, max_retries, *args, **kwargs)
                return result

            except LLMAPIError as e:
                logger.error(f"LLM API failure: {e}")
                raise UserFacingError(
                    message="AI service temporarily unavailable",
                    recovery_action="retry",
                    details=str(e)
                )

            except Exception as e:
                logger.critical(f"Unexpected error: {e}")
                raise UserFacingError(
                    message="An unexpected error occurred",
                    recovery_action="contact_support",
                    details=str(e)
                )

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


async def call_with_retry_async(
    func: Callable,
    max_retries: int,
    *args,
    **kwargs
) -> Any:
    """Execute async function with exponential backoff retry"""
    @retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((LLMAPIError, DatabaseError))
    )
    async def _retry_wrapper():
        return await func(*args, **kwargs)

    try:
        return await _retry_wrapper()
    except RetryError as e:
        # All retries exhausted
        logger.error(f"All {max_retries} retry attempts exhausted for {func.__name__}")
        raise e.last_attempt.exception()


def call_with_retry_sync(
    func: Callable,
    max_retries: int,
    *args,
    **kwargs
) -> Any:
    """Execute sync function with retry"""
    @retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((LLMAPIError, DatabaseError))
    )
    def _retry_wrapper():
        return func(*args, **kwargs)

    try:
        return _retry_wrapper()
    except RetryError as e:
        logger.error(f"All {max_retries} retry attempts exhausted")
        raise e.last_attempt.exception()


# Session state management for recovery
class SessionManager:
    """Manages session state for error recovery"""

    def __init__(self, storage_path: str = "/tmp/reasoning_sessions"):
        self.storage_path = storage_path
        import os
        os.makedirs(storage_path, exist_ok=True)

    async def save_progress(self, session_id: str, phase: int, data: dict):
        """Auto-save user progress"""
        checkpoint = {
            'session_id': session_id,
            'phase': phase,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

        filepath = f"{self.storage_path}/{session_id}_phase{phase}.json"
        with open(filepath, 'w') as f:
            json.dump(checkpoint, f)

        logger.info(f"Saved progress for session {session_id}, phase {phase}")

    async def recover_session(self, session_id: str) -> Optional[dict]:
        """Recover interrupted session"""
        import glob
        import os

        # Find all checkpoint files for this session
        pattern = f"{self.storage_path}/{session_id}_phase*.json"
        files = glob.glob(pattern)

        if not files:
            return None

        # Get latest checkpoint
        latest_file = max(files, key=os.path.getctime)

        with open(latest_file, 'r') as f:
            checkpoint = json.load(f)

        logger.info(f"Recovered session {session_id} from {latest_file}")
        return checkpoint


# Checkpoint storage (in-memory for demo, should be Redis/DB in production)
_checkpoints = {}


async def save_checkpoint(key: str, data: Any):
    """Save checkpoint for recovery"""
    _checkpoints[key] = {
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    logger.debug(f"Checkpoint saved: {key}")


async def load_checkpoint(key: str) -> Optional[Any]:
    """Load checkpoint if exists"""
    if key in _checkpoints:
        checkpoint = _checkpoints[key]
        logger.debug(f"Checkpoint loaded: {key}")
        return checkpoint['data']
    return None


# User-friendly error messages
ERROR_MESSAGES = {
    'LLM_TIMEOUT': {
        'title': "Analysis Taking Longer Than Expected",
        'message': "The AI is processing your scenario. This sometimes happens with complex analyses.",
        'actions': ["Wait and Retry", "Simplify Scenario", "Contact Support"],
        'icon': "⏳"
    },
    'DATABASE_ERROR': {
        'title': "Unable to Save Progress",
        'message': "We're experiencing technical difficulties. Your work has been saved locally.",
        'actions': ["Retry Save", "Export Locally", "Contact Support"],
        'icon': "💾"
    },
    'VALIDATION_ERROR': {
        'title': "Invalid Input",
        'message': "Please review your scenario description and ensure it meets the requirements.",
        'actions': ["Edit Input", "View Examples", "Get Help"],
        'icon': "⚠️"
    },
    'NETWORK_ERROR': {
        'title': "Connection Issue",
        'message': "Unable to connect to the server. Please check your internet connection.",
        'actions': ["Retry", "Check Connection", "Work Offline"],
        'icon': "🌐"
    }
}


def get_user_friendly_error(error_type: str) -> dict:
    """Get user-friendly error message"""
    return ERROR_MESSAGES.get(error_type, ERROR_MESSAGES['VALIDATION_ERROR'])


if __name__ == "__main__":
    print("Error Handling System initialized")
    print(f"✅ Circuit breakers ready")
    print(f"✅ Retry logic configured")
    print(f"✅ Session management active")
