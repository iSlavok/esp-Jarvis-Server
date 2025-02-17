import asyncio
import json
import os
from speechkit import model_repository, configure_credentials, creds
import time


class TTS:
    def __init__(self, websocket_manager=None):
        self.websocket_manager = websocket_manager
        configure_credentials(
            yandex_credentials=creds.YandexCredentials(
                api_key=os.getenv("YANDEX_TOKEN")
            )
        )
        self.model = model_repository.synthesis_model()
        self.model.voice = 'kirill'
        self.model.role = 'good'
        self.model.norm_type = "MAX_PEAK"
        self.model.volume = 1

    def set_websocket_manager(self, manager):
        self.websocket_manager = manager

    def send_to_websocket(self, message: str):
        if self.websocket_manager:
            asyncio.run(self.websocket_manager.broadcast(message))

    def set_voice(self, voice: str, role: str):
        self.model.voice = voice
        self.model.role = role

    def generate(self, text: str) -> str:
        t = time.time()
        result = self.model.synthesize(text, raw_format=False)
        result.export('tts.mp3', 'mp3', bitrate='64k')
        print(f"speech generated in {time.time() - t} seconds")
        return f"speech generated in {time.time() - t} seconds"
        self.send_to_websocket(json.dumps({"type": "server", "message": f"speech generated in {time.time() - t} seconds"}))
