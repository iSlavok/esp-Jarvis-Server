import asyncio
import json
import os
import subprocess
from threading import Thread
from audio import Audio
from gemini import Gemini
from mqtt import MQTTClient
from stt import STT
from web_server import WebServer
from state_manager import StateManager
from config_manager import ConfigManager
from tts import TTS


def mqtt_callback(message: str):
    if message in state_manager.states:
        state_manager.state = message
        send_state_to_websocket()
        if message == "button_recording":
            audio.new_file()
            audio.enable_write = True
        elif message == "responding":
            audio.enable_write = False
            audio.close_file()
            response = gemini.generate_from_voice(audio.file_num)
            tts.generate(response)
            state_manager.state = "speaking"
            send_state_to_websocket()
            mqtt.send_message("state speaking")
    elif message == "ready":
        state_manager.state = "waiting"
        send_state_to_websocket()
        mqtt.send_message(f"host {config_manager.host}")
        mqtt.send_message(f"volume {config_manager.volume}")


def stt_callback(text: str):
    if text is not None:
        asyncio.run(web_server.websocket_manager.broadcast(json.dumps({"type": "stt", "message": text})))
    if state_manager.state == "waiting" and text is not None:
        if "джарвис" in text.lower():
            state_manager.state = "recording"
            send_state_to_websocket()
            mqtt.send_message("state recording")
            audio.new_file()
            audio.enable_write = True
    elif state_manager.state == "recording" and text is None:
        audio.enable_write = False
        audio.close_file()
        state_manager.state = "responding"
        send_state_to_websocket()
        mqtt.send_message("state responding")
        response = gemini.generate_from_voice(audio.file_num)
        tts.generate(response)
        state_manager.state = "speaking"
        send_state_to_websocket()
        mqtt.send_message("state speaking")


def send_state_to_websocket():
    if web_server.websocket_manager:
        asyncio.run(web_server.websocket_manager.broadcast(json.dumps({"type": "state", "state": state_manager.state})))


ffmpeg_cmd = [
    "ffmpeg",
    "-loglevel", "quiet",
    "-f", "mp3",
    "-i", "pipe:0",
    "-f", "s16le",
    "-ar", "16000",
    "-ac", "1",
    "pipe:1"
]
ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

state_manager = StateManager("waiting")
config_manager = ConfigManager()
gemini = Gemini()
tts = TTS()
stt = STT(
    sample_rate=16000,
    model_path="vosk-model-small-ru-0.22",
    callback=stt_callback,
    ffmpeg_proc=ffmpeg_proc,
)
audio = Audio(
    ip="0.0.0.0",
    port=10052,
    ffmpeg_proc=ffmpeg_proc,
)
mqtt = MQTTClient(
    host="103.97.88.123",
    port=1883,
    username=os.getenv("MQTT_USERNAME"),
    password=os.getenv("MQTT_PASSWORD"),
    command_topic="device/ESP32/command",
    response_topic="device/ESP32/response",
    log_topic="device/ESP32/log",
    callback=mqtt_callback
)
web_server = WebServer(
    state_manager=state_manager,
    config_manager=config_manager,
    tts=tts,
    mqtt_client=mqtt,
    gemini=gemini
)
mqtt.set_websocket_manager(web_server.websocket_manager)
gemini.set_websocket_manager(web_server.websocket_manager)
tts.set_websocket_manager(web_server.websocket_manager)


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
    mqtt.send_message(f"state {state_manager.state}")


if __name__ == "__main__":
    main()
