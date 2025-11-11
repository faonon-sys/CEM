"""
WebSocket API for Real-Time Pipeline Notifications
===================================================

Provides WebSocket endpoints for real-time updates on trajectory projection pipelines.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional
import logging
import json

from services.websocket_manager import manager
from utils.auth import get_current_user_ws

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for trajectory projection pipeline notifications.

    Clients should connect to this endpoint to receive real-time updates
    about pipeline progress, completion, and failures.

    Args:
        websocket: WebSocket connection
        user_id: User identifier for authentication

    Message Types:
        - pipeline_progress: Progress update with step/total
        - pipeline_complete: Pipeline completed successfully
        - pipeline_failed: Pipeline failed with error details
        - ping: Keep-alive heartbeat
    """
    await manager.connect(user_id, websocket)

    try:
        # Send welcome message
        await websocket.send_json({
            'type': 'connected',
            'message': 'WebSocket connection established',
            'user_id': user_id
        })

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (mostly ping/pong)
                data = await websocket.receive_text()

                # Handle ping
                if data == 'ping':
                    await websocket.send_json({
                        'type': 'pong',
                        'message': 'Connection alive'
                    })

                # Handle status check
                elif data == 'status':
                    connection_count = manager.get_connection_count(user_id)
                    await websocket.send_json({
                        'type': 'status',
                        'user_id': user_id,
                        'active_connections': connection_count
                    })

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user_id}")
                break
            except Exception as e:
                logger.error(f"WebSocket error for user {user_id}: {e}")
                break

    finally:
        await manager.disconnect(user_id, websocket)


@router.get("/ws/connections/count")
async def get_connection_count():
    """
    Get total number of active WebSocket connections.

    Returns:
        Dictionary with connection count
    """
    return {
        'total_connections': manager.get_connection_count()
    }
