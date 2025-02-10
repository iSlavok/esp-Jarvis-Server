import asyncio
import json
import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(self, host: str, port: int, username: str, password: str, command_topic: str, response_topic: str,
                 log_topic: str, callback, websocket_manager=None):
        self.host = host
        self.port = port
        self.command_topic = command_topic
        self.response_topic = response_topic
        self.log_topic = log_topic
        self.callback = callback
        self.websocket_manager = websocket_manager
        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)
        self.client.on_message = self.on_message
        self.client.on_log = self.on_log
        self.client.connect(host, port)
        self.client.subscribe(self.response_topic)
        self.client.subscribe(self.log_topic)
        self.client.loop_start()

    def set_websocket_manager(self, manager):
        self.websocket_manager = manager

    def send_to_websocket(self, message: str):
        if self.websocket_manager:
            asyncio.run(self.websocket_manager.broadcast(message))

    def on_message(self, _client, _userdata, msg):
        if msg.topic == self.response_topic:
            self.on_response(msg.payload.decode())
        elif msg.topic == self.log_topic:
            self.on_log(msg.payload.decode())

    def on_response(self, msg: str):
        self.callback(msg)
        print(f"Received message: {msg}")

    def on_log(self, msg: str):
        if self.websocket_manager:
            self.send_to_websocket(json.dumps({"type": "client", "message": msg}))
        print(f"Received log: {msg}")

    def send_message(self, message):
        self.client.publish(self.command_topic, message)
        print(f"Sent message: {message}")
