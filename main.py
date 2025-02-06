from threading import Thread

from audio import Audio
from gemini import Gemini
from mqtt import MQTTClient
from stt import STT
from web_server import WebServer
import tts

states = ["waiting", "recording", "responding", "speaking", "button_recording"]
state = "waiting"


def audio_callback(data: list[bytes]):
    stt.queue.put(data)


def mqtt_callback(message: str):
    global state
    if message in states:
        state = message
        if message == "button_recording":
            audio.new_file()
            audio.enable_write = True
        elif message == "responding":
            audio.enable_write = False
            audio.close_file()
            response = gemini.generate_from_voice(audio.file_num)
            tts.generate(response)
            state = "speaking"
            mqtt.send_message("speaking")


def stt_callback(text: str):
    global state
    if state == "waiting" and text is not None:
        if "джарвис" in text.lower():
            state = "recording"
            mqtt.send_message("recording")
            audio.new_file()
            audio.enable_write = True
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
    sample_rate=41100,
    callback=audio_callback
)
gemini = Gemini()
mqtt = MQTTClient(
    host="162.247.153.89",
    port=1883,
    command_topic="device/ESP32/command",
    response_topic="device/ESP32/response",
    callback=mqtt_callback
)
stt = STT(
    sample_rate=41100,
    model_path="vosk-model-small-ru-0.22",
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

