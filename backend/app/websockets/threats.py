"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
"""

# Author: Kevin Zachary
# Copyright: Sentient Spire

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/ws/threats")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
