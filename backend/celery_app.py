"""
Celery Application Configuration for Sprint 5
==============================================

Configures Celery for asynchronous trajectory projection pipeline.
"""
import os
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER = REDIS_URL
CELERY_BACKEND = os.getenv("CELERY_BACKEND", "redis://localhost:6379/1")

# Create Celery application
app = Celery(
    'structured_reasoning',
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND,
    include=['tasks.trajectory_pipeline', 'tasks.phase3_pipeline']
)

# Celery Configuration
app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # Task routing
    task_routes={
        'tasks.trajectory_pipeline.*': {'queue': 'trajectory'},
        'tasks.phase3_pipeline.*': {'queue': 'phase3'},
        'tasks.exports.*': {'queue': 'exports'},
    },

    # Task execution
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,  # 9 minutes
    worker_prefetch_multiplier=1,  # Fair scheduling
    worker_max_tasks_per_child=100,  # Prevent memory leaks

    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_compression='gzip',

    # Error handling
    task_acks_late=True,  # Acknowledge after task completes
    task_reject_on_worker_lost=True,

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Task event handlers
@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Log task start"""
    logger.info(f"Task {task.name}[{task_id}] starting...")

@task_postrun.connect
def task_postrun_handler(task_id, task, *args, **kwargs):
    """Log task completion"""
    logger.info(f"Task {task.name}[{task_id}] completed successfully")

@task_failure.connect
def task_failure_handler(task_id, exception, *args, **kwargs):
    """Log task failure"""
    logger.error(f"Task [{task_id}] failed with exception: {exception}")

if __name__ == '__main__':
    app.start()
