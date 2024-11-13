from threading import Thread

from audio import Audio
from gemini import Gemini
from mqtt import MQTTClient
from stt import STT
from web_server import WebServer
import tts

with open('secret.txt', 'r') as file:
    gemini_token = file.readline().strip()

states = ["waiting", "recording", "responding", "speaking"]
state = "waiting"


def audio_callback(data: list[int]):
    stt.queue.put(data)


def mqtt_callback(message: str):
    global state
    if message in states:
        state = message
        match message:
            case "waiting":
                pass
            case "recording":
                pass
            case "responding":
                pass
            case "speaking":
                pass
    elif message == "start":
        state = "waiting"
        mqtt.send_message("waiting")
        audio.enable = True
        audio.close_file()


def stt_callback(text: str | None):
    global state
    if state == "waiting" and text is not None:
        if "джарвис" in text:
            state = "recording"
            mqtt.send_message("recording")
            audio.new_file()
    elif state == "recording" and text is None:
        audio.enable_write = False
        audio.close_file()
        state = "responding"
        mqtt.send_message("responding")
        response = gemini.generate_from_voice(audio.file_num)
        tts.generate(response)
        state = "speaking"
        mqtt.send_message("speaking")


audio = Audio(
    ip="0.0.0.0",
    port=10052,
    gain=15,
    chunk_size=1024,
    sample_rate=16000,
    callback=audio_callback
)
gemini = Gemini(
    ""
)
mqtt = MQTTClient(
    host="103.97.88.123",
    port=1883,
    command_topic="device/ESP32/command",
    response_topic="device/ESP32/response",
    callback=mqtt_callback
)
stt = STT(
    sample_rate=16000,
    model_path="./vosk-model-small-ru-0.22",
    callback=stt_callback
)
web_server = WebServer()


def main():
    audio_thread = Thread(target=audio.streaming_from_udp)
    audio_thread.start()
    stt_thread = Thread(target=stt.process_audio)
    stt_thread.start()
    web_server_thread = Thread(target=web_server.start)
    web_server_thread.start()
    audio_thread.join()
    stt_thread.join()
    web_server_thread.join()
    mqtt.send_message(state)


if __name__ == "__main__":
    main()
