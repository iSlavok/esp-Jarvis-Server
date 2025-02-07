from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json

from pydantic import BaseModel
from starlette.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


class StateUpdate(BaseModel):
    new_state: str


state = "default_state"
possible_states = ["default_state", "state1", "state2"]

client_config = {"audio_url": "dawudhawudhawuhda", "volume": 50}
server_config = {"voice": "default_voice", "role": "default_role"}
voices = ["default_voice", "voice1", "voice2"]
roles_by_voice = {
    "default_voice": ["default_role", "role1"],
    "voice1": ["role2", "role3"],
    "voice2": ["role4", "role5"],
}


# Менеджер подключений для работы с WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


# Главная страница
@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Эндпоинты для получения данных
@app.get("/states")
async def get_states():
    return {"states": possible_states, "current_state": state}


@app.get("/voices")
async def get_voices():
    return {"voices": voices}


@app.get("/roles")
async def get_roles(voice: str):
    return {"roles": roles_by_voice.get(voice, [])}


@app.get("/client_config")
async def get_client_config():
    return client_config


@app.get("/server_config")
async def get_server_config():
    return server_config


@app.post("/update_state")
async def update_state(data: StateUpdate):
    global state
    state = data.new_state
    await manager.broadcast(json.dumps({"type": "state_update", "state": state}))
    return {"status": "ok", "state": state}


@app.post("/update_client_config")
async def update_client_config(config: dict):
    global client_config
    client_config.update(config)
    await manager.broadcast(json.dumps({"type": "client_config_update", "config": client_config}))
    return {"status": "ok", "config": client_config}


@app.post("/update_server_config")
async def update_server_config(config: dict):
    global server_config
    server_config.update(config)
    await manager.broadcast(json.dumps({"type": "server_config_update", "config": server_config}))
    return {"status": "ok", "config": server_config}


# WebSocket-эндпоинт для обмена данными в реальном времени
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Здесь можно обрабатывать входящие сообщения от клиента
            message = json.loads(data)
            if message["type"] == "chat_message":
                print(message["message"])
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# # Запуск сервера
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=5002)
