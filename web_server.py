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
from config_manager import ConfigManager
from gemini import Gemini
from state_manager import StateManager
from tts import TTS


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


class HostUpdate(BaseModel):
    host: str


class VolumeUpdate(BaseModel):
    volume: int


class VoiceUpdate(BaseModel):
    voice: str
    role: str


class WebServer:
    def __init__(self, state_manager: StateManager, config_manager: ConfigManager, tts: TTS, mqtt_client, gemini: Gemini):
        self.state_manager = state_manager
        self.config_manager = config_manager
        self.mqtt_client = mqtt_client
        self.tts = tts
        self.gemini = gemini
        self.app = FastAPI()
        self.setup_routes()
        self.manager = ConnectionManager()
        self.templates = Jinja2Templates(directory="templates")
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

    @property
    def websocket_manager(self):
        return self.manager

    def setup_routes(self):
        @self.app.get("/audio-stream")
        async def audio_file():
            if os.path.exists("tts.mp3"):
                return FileResponse("tts.mp3", media_type="audio/mp3")
            return FileResponse("error.mp3", media_type="audio/mp3")

        @self.app.get("/", response_class=HTMLResponse)
        async def get(request: Request):
            return self.templates.TemplateResponse("index.html", {"request": request})

        @self.app.get("/roles")
        async def get_roles(voice: str):
            return {"roles": self.config_manager.voices.get(voice, [])}

        @self.app.get("/config")
        async def get_config():
            return {
                "audio_url": self.config_manager.host,
                "volume": self.config_manager.volume,
                "voices": list(self.config_manager.voices.keys()),
                "voice": self.config_manager.voice,
                "role": self.config_manager.role,
                "states": self.state_manager.states,
                "current_state": self.state_manager.state
            }

        @self.app.post("/update_state")
        async def update_state(data: StateUpdate):
            if data.new_state != self.state_manager.state:
                self.state_manager.state = data.new_state
                self.mqtt_client.send_message(f"state {data.new_state}")
                await self.manager.broadcast(json.dumps({"type": "server", "message": f"State updated to {data.new_state}"}))
            return {"status": "ok"}

        @self.app.post("/update_host")
        async def update_host(data: HostUpdate):
            if data.host != self.config_manager.host:
                self.config_manager.host = data.host
                self.mqtt_client.send_message(f"host {data.host}")
            return {"status": "ok"}

        @self.app.post("/update_volume")
        async def update_volume(data: VolumeUpdate):
            if data.volume != self.config_manager.volume:
                self.config_manager.volume = data.volume
                self.mqtt_client.send_message(f"volume {data.volume}")
            return {"status": "ok"}

        @self.app.post("/update_voice")
        async def update_voice(voice: VoiceUpdate):
            if voice.voice != self.config_manager.voice or voice.role != self.config_manager.role:
                self.config_manager.voice = voice.voice
                self.config_manager.role = voice.role
                self.tts.set_voice(voice.voice, voice.role)
                await self.manager.broadcast(json.dumps({"type": "server", "message": f"Voice updated to {voice.voice}, {voice.role}"}))
            return {"status": "ok"}

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    if message["type"] == "chat_message":
                        self.gemini.generate_from_text(message["message"])
            except WebSocketDisconnect:
                self.manager.disconnect(websocket)

    def start(self):
        uvicorn.run(self.app, host="0.0.0.0", port=5252)
