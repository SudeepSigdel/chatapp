from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from sqlmodel import Session
from app import oauth2, database, models

router = APIRouter(
    tags=["Websocket"]
)

class ConnectionManager:
    def __init__(self):
        self.active_connections : List[models.Connection] = []
    def connect(self, connection: models.Connection):
        self.active_connections.append(connection)
    def disconnect(self, connection: models.Connection):
        self.active_connections.remove(connection)
    async def broadcast(self, message:str):
        disconnected = []

        for connection in self.active_connections:
            websocket = connection.websocket

            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()


@router.websocket("/ws")
async def Websocket(websocket: WebSocket):
    
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    db = Session(database.engine)
    user = oauth2.get_current_user(db, token)
    if user is None:
        await websocket.close(code=1008)
        return
    
    await websocket.accept()
    
    connection = models.Connection(
        websocket, 
        user.id,
        user.name
    )
    
    manager.connect(connection)
    await manager.broadcast(f"{user.name} has joined")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{user.name} says: {data}")
    except WebSocketDisconnect:
        
        manager.disconnect(connection)
        await manager.broadcast(f"{user.name} has left the chat")
    finally:
        db.close()
