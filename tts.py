from gtts import gTTS


def generate(text: str):
    tts = gTTS(text, lang="ru")
    tts.save('tts.mp3')
