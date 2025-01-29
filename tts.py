from speechkit import model_repository, configure_credentials, creds
import time

configure_credentials(
    yandex_credentials=creds.YandexCredentials(
        api_key='AQVNzAjp2K-NS2h4O4PwyrP0m10POehWU34TTTU1'
    )
)
model = model_repository.synthesis_model()
model.voice = 'kirill'
model.role = 'good'


def generate(text):
    t = time.time()
    result = model.synthesize(text, raw_format=False)
    result.export('tts.wav', 'wav')
    print(f"speech generated in {time.time() - t} seconds")
