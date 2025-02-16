from vosk import Model, KaldiRecognizer
from queue import Queue
import numpy
import json


class STT:
    def __init__(self, sample_rate: int, model_path: str, callback, ffmpeg_proc):
        try:
            self.model = Model(model_path)
            print("Vosk successfully loaded")
        except Exception as e:
            print(f"Error Vosk loading: {e}")
            raise
        self.callback = callback
        self.recognizer = KaldiRecognizer(self.model, sample_rate)
        self.ffmpeg_proc = ffmpeg_proc

    def process_audio(self):
        while True:
            try:
                pcm_data = self.ffmpeg_proc.stdout.read(4096)
                if not pcm_data:
                    break
                if self.recognizer.AcceptWaveform(pcm_data):
                    result = json.loads(self.recognizer.Result())
                    if result.get("text", "").strip():
                        recognized_text = result["text"]
                        self.callback(recognized_text)
                    else:
                        self.callback(None)
            except Exception as e:
                self.callback(str(e))
                print(f"Ошибка в процессе распознавания: {e}")
