from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
import os


class WebServer:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/audio-stream")
        async def audio_file():
            if os.path.exists("tts.mp3"):
                return FileResponse("tts.mp3", media_type="audio/mp3")
            return FileResponse("error.mp3", media_type="audio/mp3")

    def start(self):
        uvicorn.run(self.app, host="0.0.0.0", port=5000)
