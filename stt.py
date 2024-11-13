from vosk import Model, KaldiRecognizer
from queue import Queue
import numpy
import json


class STT:
    def __init__(self, sample_rate: int, model_path: str, callback):
        try:
            self.model = Model(model_path)
            print("Vosk successfully loaded")
        except Exception as e:
            print(f"Error Vosk loading: {e}")
            raise
        self.queue = Queue()
        self.callback = callback
        self.recognizer = KaldiRecognizer(self.model, sample_rate)

    def process_audio(self):
        while True:
            try:
                if not self.queue.empty():
                    audio_data = self.queue.get()
                    if isinstance(audio_data, bytes):
                        audio_array = numpy.frombuffer(audio_data, dtype=numpy.int16)
                    else:
                        audio_array = numpy.array(audio_data, dtype=numpy.int16)
                    if self.recognizer.AcceptWaveform(audio_array.tobytes()):
                        result = json.loads(self.recognizer.Result())
                        if result.get("text", "").strip():
                            recognized_text = result["text"]
                            self.callback(recognized_text)
                        else:
                            self.callback(None)
            except Exception as e:
                print(f"Ошибка в процессе распознавания: {e}")