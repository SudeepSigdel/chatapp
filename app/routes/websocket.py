import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from app import oauth2, database, models

router = APIRouter(
    tags=["Websocket"]
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, set[models.Connection]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, connection: models.Connection):
        async with self.lock:
            self.active_connections.setdefault(connection.user_id, set()).add(connection)

    async def disconnect(self, connection: models.Connection):
        async with self.lock:
            user_connections = manager.active_connections.get(
                connection.user_id)

            if not user_connections:
                return

            user_connections.discard(connection)

            if not user_connections:
                del self.active_connections[connection.user_id]

    async def private_message(self, user_id: int, message: str):
        connections = self.active_connections.get(user_id)
        if not connections:
            return
        for connection in connections:
            websocket = connection.websocket
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        disconnected = []

        for connection in self.active_connections.values():
            for conn in connection:
                websocket = conn.websocket

                try:
                    await websocket.send_text(message)
                except Exception:
                    disconnected.append(conn)

        for conn in disconnected:
            await self.disconnect(conn)


manager = ConnectionManager()


@router.websocket("/ws")
async def Websocket(websocket: WebSocket):

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    # target_user_id = websocket.query_params.get("user_id")
    # try:
    #     target_user_id = int(target_user_id) if target_user_id else None
    # except Exception:
    #     await websocket.close(code=1008)
    #     return

    db = Session(database.engine)
    user = oauth2.get_current_user(db, token)
    if user is None:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    connection = models.Connection(
        websocket=websocket,
        user_id=user.id,
        username=user.name
    )

    await manager.connect(connection)
    await manager.broadcast(f"{user.name} has joined")

    try:
        while True:
            data = await websocket.receive_text()
            message = f"{user.name} says: {data}"

            # if target_user_id:
            #     if user.id != target_user_id: await manager.private_message(user.id, message) #type: ignore
            #     await manager.private_message(target_user_id, message)

            # else:
            await manager.broadcast(message)
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(connection)
        await manager.broadcast(f"{user.name} has left the chat")
        db.close()