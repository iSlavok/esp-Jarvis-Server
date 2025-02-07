import os
import pathlib
import time
import google.generativeai as genai


class Gemini:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_TOKEN"))
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite-preview-02-05",
            system_instruction="Ты ассистент по имени 'Джарвис'. Общайся с пользователями, отвечай текстом, старайся без эмодзи, спец символов и другого форматирования текста так как твои ответы будут переводиться в голос.",
            generation_config=genai.GenerationConfig(
                max_output_tokens=500,
                temperature=1.0,
            ),
        )
        self.chat = model.start_chat()

    def generate_from_voice(self, file_num: int):
        t = time.time()
        result = self.chat.send_message(
            ["esp32:", {
                "mime_type": "audio/wav",
                "data": pathlib.Path(f'sounds/{file_num}.wav').read_bytes()
            }]
        )
        print(f"response generated in {time.time() - t} seconds")
        return result.text

    def generate_from_text(self, prompt: str):
        result = self.chat.send_message(
            prompt
        )
        return result.text
