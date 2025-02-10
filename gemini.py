import asyncio
import json
import pathlib
import time
from google import genai
from google.genai import types


class Gemini:
    def __init__(self, websocket_manager=None):
        self.websocket_manager = websocket_manager
        self.client = genai.Client()
        self.chat = self.create_chat()

    def set_websocket_manager(self, manager):
        self.websocket_manager = manager

    def send_to_websocket(self, message: str):
        if self.websocket_manager:
            asyncio.run(self.websocket_manager.broadcast(message))

    def send_to_websocket_task(self, message: str):
        if self.websocket_manager:
            asyncio.create_task(self.websocket_manager.broadcast(message))

    def generate_from_voice(self, file_num: int) -> str:
        t = time.time()
        result = self.chat.send_message(
            [
                ".",
                types.Part.from_bytes(
                    data=pathlib.Path(f'sounds/{file_num}.wav').read_bytes(),
                    mime_type='audio/wav',
                )
            ]
        )
        print(f"response generated in {time.time() - t} seconds")
        self.send_to_websocket(json.dumps({"type": "server", "message": f"response generated in {time.time() - t} seconds"}))
        self.send_to_websocket(json.dumps({"type": "chat", "message": result.text}))
        return result.text

    def generate_from_text(self, prompt: str) -> str:
        time_start = time.time()
        result = self.chat.send_message(
            prompt
        )
        print(f"response generated in {time.time() - time_start} seconds")
        self.send_to_websocket_task(json.dumps({"type": "server", "message": f"response generated in {time.time() - time_start} seconds"}))
        self.send_to_websocket_task(json.dumps({"type": "chat", "message": result.text}))
        return result.text

    def create_chat(self):
        return self.client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction="Ты ассистент по имени 'Джарвис'. Общайся с пользователями, отвечай текстом, старайся без эмодзи, спец символов и другого форматирования текста так как твои ответы будут переводиться в голос.",
                temperature=1.0,
                max_output_tokens=500,
                tools=[types.Tool(
                    google_search=types.GoogleSearch()
                )]
            )
        )
