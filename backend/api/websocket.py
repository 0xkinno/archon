import json
import logging
from typing import List, Dict, Any, Set
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("archon.websocket")
router = APIRouter()


class WebSocketManager:
    """Manages active browser connections and broadcasts real-time agent/incident events."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total active: {len(self.active_connections)}")
        
        # Send initial handshake event
        await self.send_personal_message(
            websocket,
            {
                "type": "connection.established",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "status": "connected",
                    "server": "ARCHON Enterprise Operations Engine",
                    "geap_fleet_status": "ONLINE",
                }
            }
        )

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining: {len(self.active_connections)}")

    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        try:
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.warning(f"Failed to send personal WebSocket message: {e}")

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcasts a structured event across all connected frontend dashboards."""
        payload = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        message_str = json.dumps(payload, default=str)
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.debug(f"Broadcasting to client failed: {e}")
                disconnected.add(connection)

        for dead_conn in disconnected:
            self.disconnect(dead_conn)


ws_manager = WebSocketManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "ping":
                    await ws_manager.send_personal_message(
                        websocket,
                        {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                    )
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
