"""
WebSocket Connection Manager for Real-Time Collaboration

Manages WebSocket connections for demo mode collaboration features.
Supports multi-user demo sessions with real-time synchronization.
"""

from typing import Dict, Set, Optional, Any
from fastapi import WebSocket
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time collaboration"""
    
    def __init__(self):
        # Active connections by session_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # User info by connection
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
        # Session metadata
        self.session_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(
        self, 
        websocket: WebSocket, 
        session_id: str, 
        user_id: Optional[str] = None,
        user_name: Optional[str] = None
    ):
        """Accept a new WebSocket connection and add to session"""
        await websocket.accept()
        
        # Initialize session if it doesn't exist
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
            self.session_metadata[session_id] = {
                "created_at": datetime.utcnow().isoformat(),
                "participant_count": 0
            }
        
        # Add connection to session
        self.active_connections[session_id].add(websocket)
        
        # Store connection info
        self.connection_info[websocket] = {
            "session_id": session_id,
            "user_id": user_id or "anonymous",
            "user_name": user_name or "Guest",
            "connected_at": datetime.utcnow().isoformat()
        }
        
        # Update participant count
        self.session_metadata[session_id]["participant_count"] = len(
            self.active_connections[session_id]
        )
        
        logger.info(
            f"New connection to session {session_id}. "
            f"Total participants: {self.session_metadata[session_id]['participant_count']}"
        )
        
        # Notify other participants about new user
        await self.broadcast_to_session(
            session_id,
            {
                "type": "user_joined",
                "user_id": user_id or "anonymous",
                "user_name": user_name or "Guest",
                "participant_count": self.session_metadata[session_id]["participant_count"],
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude=websocket
        )
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket not in self.connection_info:
            return
        
        connection_info = self.connection_info[websocket]
        session_id = connection_info["session_id"]
        
        # Remove from session
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            # Update participant count
            if self.active_connections[session_id]:
                self.session_metadata[session_id]["participant_count"] = len(
                    self.active_connections[session_id]
                )
            else:
                # Clean up empty session
                del self.active_connections[session_id]
                del self.session_metadata[session_id]
        
        # Remove connection info
        del self.connection_info[websocket]
        
        logger.info(f"Connection disconnected from session {session_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_session(
        self, 
        session_id: str, 
        message: dict,
        exclude: Optional[WebSocket] = None
    ):
        """Broadcast a message to all connections in a session"""
        if session_id not in self.active_connections:
            return
        
        # Get list of connections to avoid modification during iteration
        connections = list(self.active_connections[session_id])
        
        for connection in connections:
            if connection != exclude:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")
                    # Remove failed connection
                    self.disconnect(connection)
    
    async def broadcast_event(
        self,
        session_id: str,
        event_type: str,
        data: dict,
        exclude: Optional[WebSocket] = None
    ):
        """Broadcast a typed event to a session"""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_session(session_id, message, exclude)
    
    def get_session_participants(self, session_id: str) -> list:
        """Get list of participants in a session"""
        if session_id not in self.active_connections:
            return []
        
        participants = []
        for connection in self.active_connections[session_id]:
            if connection in self.connection_info:
                info = self.connection_info[connection]
                participants.append({
                    "user_id": info["user_id"],
                    "user_name": info["user_name"],
                    "connected_at": info["connected_at"]
                })
        
        return participants
    
    def get_active_sessions(self) -> list:
        """Get list of all active sessions"""
        sessions = []
        for session_id, metadata in self.session_metadata.items():
            sessions.append({
                "session_id": session_id,
                "participant_count": metadata["participant_count"],
                "created_at": metadata["created_at"]
            })
        return sessions


# Global connection manager instance
manager = ConnectionManager()
