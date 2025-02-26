# ESP-Jarvis-Server

Server side of a voice assistant that works with an ESP32 device. This is a school project created for educational purposes and personal use.

## Project Overview

This project implements the server component of a "Jarvis" voice assistant system:

- Voice command recognition ("джарвис" wake word)
- Text-to-speech capabilities via Yandex SpeechKit
- Integration with Gemini AI for responses
- ESP32 device communication via MQTT
- Web interface for monitoring and configuration

## Technical Details

- **Backend:** Python
- **Frontend:** JavaScript, CSS, HTML
- **Voice Processing:** VOSK for speech-to-text, Yandex SpeechKit for text-to-speech
- **Communication:** MQTT for ESP32 device control
- **AI Integration:** Google's Gemini for response generation

## Features

- Voice command recognition and processing
- Real-time state management (waiting, recording, responding, speaking)
- Web control panel with various customization options
- Voice settings configuration (voice selection, role, volume)
- Chat interface for direct interaction with the AI model

## Related Projects

This is the server component. For the ESP32 client device code, see [ESP-Jarvis-Client](https://github.com/iSlavok/esp-Jarvis-Client).

## Note

This project is published for portfolio and educational purposes only. It was created as a school project and is not intended for production use.