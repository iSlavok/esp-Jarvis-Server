import pathlib
import time
import google.generativeai as genai


class Gemini:
    def __init__(self, token):
        genai.configure(api_key=token)
        model = genai.GenerativeModel("gemini-2.0-flash-exp",
                                      system_instruction="Ты голосовой помощник по имени 'Джарвис'. Общайся с пользователями, отвечай текстом, старайся без эмодзи.")
        self.chat = model.start_chat()

    def generate_from_voice(self, file_num: int):
        t = time.time()
        result = self.chat.send_message(
            ["a", {
                "mime_type": "audio/wav",
                "data": pathlib.Path(f'sounds/{file_num}.wav').read_bytes()
            }],
            generation_config=genai.GenerationConfig(
                max_output_tokens=500,
                temperature=0.5,
            )
        )
        print(f"voice generated in {time.time() - t} seconds")
        return result.text

    def generate_from_text(self, prompt: str):
        result = self.chat.send_message(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=100,
                temperature=1,
            )
        )
        return result.text
