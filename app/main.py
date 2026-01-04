from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .routes import users, websocket, auth
from fastapi.middleware.cors import CORSMiddleware


from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(websocket.router)
app.include_router(auth.router)

app.mount("/static", StaticFiles(directory="chatsystem-frontend"), name="static")

@app.get("/")
def index():
    with open("chatsystem-frontend/index.html","r") as f:
        return HTMLResponse(f.read())