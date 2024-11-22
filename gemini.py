import pathlib
import google.generativeai as genai


class Gemini:
    def __init__(self, token):
        genai.configure(api_key=token)
        model = genai.GenerativeModel("gemini-1.5-flash",
                                      system_instruction="Ты голосовой помощник по имени 'Джарвис'. Общайся с пользователями, отвечай текстом, старайся без эмодзи.")
        self.chat = model.start_chat()

    def generate_from_voice(self, file_num: int):
        result = self.chat.send_message(
            ["", {
                "mime_type": "audio/wav",
                "data": pathlib.Path(f'sounds/{file_num}.wav').read_bytes()
            }],
            generation_config=genai.GenerationConfig(
                max_output_tokens=100,
                temperature=0.5,
            )
        )
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
