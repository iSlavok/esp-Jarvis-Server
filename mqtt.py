import os

import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(self, host: str, port: int, username: str, password: str, command_topic: str, response_topic: str, callback):
        self.host = host
        self.port = port
        self.command_topic = command_topic
        self.response_topic = response_topic
        self.callback = callback
        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)
        self.client.on_message = self.on_message
        self.client.connect(host, port)
        self.client.subscribe(self.response_topic)
        self.client.loop_start()

    def on_message(self, _client, _userdata, msg):
        self.callback(msg.payload.decode())
        print(f"Received message: {msg.payload.decode()}")

    def send_message(self, message):
        self.client.publish(self.command_topic, message)
        print(f"Sent message: {message}")
