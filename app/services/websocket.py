# app/services/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Set
import json
import asyncio
from app.models.token import WebSocketMessage

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for topic in self.subscriptions:
            self.subscriptions[topic].discard(websocket)
    
    def subscribe(self, websocket: WebSocket, topic: str):
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        self.subscriptions[topic].add(websocket)
    
    async def broadcast_to_topic(self, topic: str, message: dict):
        if topic not in self.subscriptions:
            return
        
        disconnected = []
        for websocket in self.subscriptions[topic]:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.disconnect(ws)
    
    async def broadcast_all(self, message: dict):
        disconnected = []
        for websocket in self.active_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                disconnected.append(websocket)
        
        for ws in disconnected:
            self.disconnect(ws)

websocket_manager = WebSocketManager()
