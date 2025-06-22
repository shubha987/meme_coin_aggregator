from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket import websocket_manager
import json

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                topic = message.get("topic", "tokens")
                websocket_manager.subscribe(websocket, topic)
                await websocket.send_text(json.dumps({
                    "type": "subscription_confirmed",
                    "topic": topic
                }))
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)