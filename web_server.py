import json
from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
import os
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect, WebSocket
from state_manager import StateManager
from mqtt import MQTTClient


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


class StateUpdate(BaseModel):
    new_state: str


class VolumeUpdate(BaseModel):
    volume: int


class WebServer:
    def __init__(self, state_manager: StateManager, mqtt_client: MQTTClient):
        self.state_manager = state_manager
        self.mqtt_client = mqtt_client
        self.app = FastAPI()
        self.setup_routes()
        self.manager = ConnectionManager()
        self.templates = Jinja2Templates(directory="templates")
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

    def setup_routes(self):
        @self.app.get("/audio-stream")
        async def audio_file():
            if os.path.exists("tts.mp3"):
                return FileResponse("tts.mp3", media_type="audio/mp3")
            return FileResponse("error.mp3", media_type="audio/mp3")

        @self.app.get("/", response_class=HTMLResponse)
        async def get(request: Request):
            return self.templates.TemplateResponse("index.html", {"request": request})

        @self.app.get("/states")
        async def get_states():
            return {"states": possible_states, "current_state": state}

        @self.app.get("/voices")
        async def get_voices():
            return {"voices": voices}

        @self.app.get("/roles")
        async def get_roles(voice: str):
            return {"roles": roles_by_voice.get(voice, [])}

        @self.app.get("/client_config")
        async def get_client_config():
            return client_config

        @self.app.get("/server_config")
        async def get_server_config():
            return server_config

        @self.app.post("/update_state")
        async def update_state(data: StateUpdate):
            global state
            state = data.new_state
            await self.manager.broadcast(json.dumps({"type": "state", "state": state}))
            return {"status": "ok"}

        @self.app.post("/update_volume")
        async def update_volume(data: VolumeUpdate):
            global client_config
            volume = data.volume
            client_config["volume"] = volume
            return {"status": "ok"}

        @self.app.post("/update_client_config")
        async def update_client_config(config: dict):
            global client_config
            client_config.update(config)
            await self.manager.broadcast(json.dumps({"type": ""}))
            return {"status": "ok", "config": client_config}

        @self.app.post("/update_server_config")
        async def update_server_config(config: dict):
            global server_config
            server_config.update(config)
            await self.manager.broadcast(json.dumps({"type": "server_config_update", "config": server_config}))
            return {"status": "ok", "config": server_config}

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    if message["type"] == "chat_message":
                        pass
            except WebSocketDisconnect:
                self.manager.disconnect(websocket)

    def start(self):
        uvicorn.run(self.app, host="0.0.0.0", port=5000)
