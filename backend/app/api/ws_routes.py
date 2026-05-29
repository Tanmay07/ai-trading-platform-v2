from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from typing import List

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time market updates and system notifications.
    Clients connecting to this endpoint will receive JSON payloads.
    """
    await manager.connect(websocket)
    try:
        # Send initial connection success message
        await websocket.send_json({"type": "system", "message": "Connected to AI Trading Platform WS"})
        
        while True:
            # We wait for messages from the client (e.g. subscribe to a symbol)
            data = await websocket.receive_text()
            # Echo back an acknowledgement
            await websocket.send_json({"type": "ack", "data": data})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task simulator for market updates (for demonstration purposes)
async def market_update_simulator():
    """Simulates real-time market price updates being broadcasted."""
    while True:
        await asyncio.sleep(5)  # Send update every 5 seconds
        if manager.active_connections:
            # Send a heartbeat/update
            import random
            await manager.broadcast({
                "type": "market_update",
                "symbol": "RELIANCE.NS",
                "price": round(random.uniform(2500, 2600), 2)
            })
