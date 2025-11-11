"""
WebSocket Manager for Real-Time Pipeline Notifications
=======================================================

Manages WebSocket connections and sends real-time updates to users
about trajectory projection pipeline progress.
"""
import logging
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
import json

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time notifications.

    Supports multiple connections per user and broadcasts messages
    to all user connections simultaneously.
    """

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection.

        Args:
            user_id: User identifier
            websocket: WebSocket connection
        """
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")

    async def disconnect(self, user_id: str, websocket: WebSocket):
        """
        Unregister a WebSocket connection.

        Args:
            user_id: User identifier
            websocket: WebSocket connection to remove
        """
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"WebSocket disconnected for user {user_id}. Remaining: {len(self.active_connections[user_id])}")

            # Clean up empty user entries
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, user_id: str, message: Dict):
        """
        Send message to all connections for a specific user.

        Args:
            user_id: User identifier
            message: Message dictionary to send
        """
        if user_id not in self.active_connections:
            logger.warning(f"No active connections for user {user_id}")
            return

        disconnected = []

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            await self.disconnect(user_id, conn)

    async def broadcast(self, message: Dict):
        """
        Broadcast message to all connected users.

        Args:
            message: Message dictionary to broadcast
        """
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(user_id, message)

    def get_connection_count(self, user_id: str = None) -> int:
        """
        Get count of active connections.

        Args:
            user_id: If provided, return count for specific user

        Returns:
            Number of active connections
        """
        if user_id:
            return len(self.active_connections.get(user_id, []))
        else:
            return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager instance
manager = ConnectionManager()


async def notify_pipeline_progress(
    user_id: str,
    task_id: str,
    state: str,
    progress: Dict
):
    """
    Send pipeline progress notification to user.

    Args:
        user_id: User to notify
        task_id: Celery task ID
        state: Current task state
        progress: Progress metadata dictionary
    """
    message = {
        'type': 'pipeline_progress',
        'task_id': task_id,
        'state': state,
        'progress': progress,
        'timestamp': progress.get('timestamp')
    }

    await manager.send_personal_message(user_id, message)


async def notify_pipeline_complete(
    user_id: str,
    task_id: str,
    trajectory_id: str,
    result: Dict
):
    """
    Send pipeline completion notification to user.

    Args:
        user_id: User to notify
        task_id: Celery task ID
        trajectory_id: Generated trajectory ID
        result: Task result dictionary
    """
    message = {
        'type': 'pipeline_complete',
        'task_id': task_id,
        'trajectory_id': trajectory_id,
        'result': result
    }

    await manager.send_personal_message(user_id, message)


async def notify_pipeline_failure(
    user_id: str,
    task_id: str,
    error: str,
    error_message: str
):
    """
    Send pipeline failure notification to user.

    Args:
        user_id: User to notify
        task_id: Celery task ID
        error: Error type
        error_message: Error message
    """
    message = {
        'type': 'pipeline_failed',
        'task_id': task_id,
        'error': error,
        'message': error_message
    }

    await manager.send_personal_message(user_id, message)
