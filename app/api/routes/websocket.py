"""
WebSocket API Routes for Real-Time Collaboration

Provides WebSocket endpoints for demo mode collaboration and real-time features.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional
import logging
import json

from app.core.enforcement import require_access

# Import the connection manager from backend/shared
import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent.parent.parent / "backend" / "shared"
sys.path.insert(0, str(backend_path))

from websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/demo/{session_id}")
async def demo_collaboration_websocket(
    websocket: WebSocket,
    session_id: str,
    user_id: Optional[str] = Query(None),
    user_name: Optional[str] = Query("Guest")
):
    """
    WebSocket endpoint for demo mode collaboration.
    
    Enables real-time synchronization between multiple users viewing the same demo session.
    
    Events supported:
    - user_joined: When a new user joins the session
    - user_left: When a user leaves the session
    - navigation: When a user navigates to a different page
    - interaction: When a user interacts with demo elements
    - cursor_move: Real-time cursor position updates
    - demo_state: Synchronize demo state changes
    """
    await manager.connect(websocket, session_id, user_id, user_name)
    
    try:
        # Send initial session info
        await manager.send_personal_message({
            "type": "connected",
            "session_id": session_id,
            "participants": manager.get_session_participants(session_id),
            "message": "Connected to demo collaboration session"
        }, websocket)
        
        # Listen for messages
        while True:
            data = await websocket.receive_json()
            
            # Handle different event types
            event_type = data.get("type")
            
            if event_type == "navigation":
                # Broadcast navigation event to other participants
                await manager.broadcast_event(
                    session_id,
                    "navigation",
                    {
                        "user_id": user_id or "anonymous",
                        "user_name": user_name,
                        "path": data.get("path"),
                        "page_title": data.get("page_title")
                    },
                    exclude=websocket
                )
            
            elif event_type == "interaction":
                # Broadcast user interactions
                await manager.broadcast_event(
                    session_id,
                    "interaction",
                    {
                        "user_id": user_id or "anonymous",
                        "user_name": user_name,
                        "action": data.get("action"),
                        "element": data.get("element"),
                        "details": data.get("details")
                    },
                    exclude=websocket
                )
            
            elif event_type == "cursor_move":
                # Broadcast cursor position (throttled on client side)
                await manager.broadcast_event(
                    session_id,
                    "cursor_move",
                    {
                        "user_id": user_id or "anonymous",
                        "user_name": user_name,
                        "x": data.get("x"),
                        "y": data.get("y")
                    },
                    exclude=websocket
                )
            
            elif event_type == "demo_state":
                # Synchronize demo state changes
                await manager.broadcast_event(
                    session_id,
                    "demo_state",
                    {
                        "user_id": user_id or "anonymous",
                        "user_name": user_name,
                        "state": data.get("state"),
                        "changes": data.get("changes")
                    },
                    exclude=websocket
                )
            
            elif event_type == "message":
                # Chat messages between participants
                await manager.broadcast_event(
                    session_id,
                    "message",
                    {
                        "user_id": user_id or "anonymous",
                        "user_name": user_name,
                        "message": data.get("message")
                    },
                    exclude=websocket
                )
            
            else:
                # Unknown event type
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown event type: {event_type}"
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # Notify other participants
        await manager.broadcast_event(
            session_id,
            "user_left",
            {
                "user_id": user_id or "anonymous",
                "user_name": user_name,
                "participant_count": len(manager.get_session_participants(session_id))
            }
        )
        logger.info(f"Client {user_id or 'anonymous'} disconnected from session {session_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/ws/sessions")
async def get_active_sessions(
    auth: tuple = Depends(require_access("websocket", "read"))
):
    """Get list of all active collaboration sessions"""
    current_user, org_id = auth
    
    return {
        "sessions": manager.get_active_sessions()
    }


@router.get("/ws/sessions/{session_id}/participants")
async def get_session_participants(
    session_id: str,
    auth: tuple = Depends(require_access("websocket", "read"))
):
    """Get list of participants in a specific session"""
    current_user, org_id = auth
    
    return {
        "session_id": session_id,
        "participants": manager.get_session_participants(session_id)
    }
