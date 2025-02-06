import os

from speechkit import model_repository, configure_credentials, creds
import time

configure_credentials(
    yandex_credentials=creds.YandexCredentials(
        api_key=os.getenv("YANDEX_TOKEN")
    )
)
model = model_repository.synthesis_model()
model.voice = 'kirill'
model.role = 'good'


def generate(text: str):
    t = time.time()
    result = model.synthesize(text, raw_format=False)
    result.export('tts.mp3', 'mp3', bitrate='128k')
    print(f"speech generated in {time.time() - t} seconds")
