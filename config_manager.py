from threading import Lock


class ConfigManager:
    def __init__(self):
        self._voice = "kirill"
        self._role = "good"
        self._volume = 50
        self._host = "http://localhost:5000/audio-stream"
        self._lock = Lock()
        self._voices = {
            "alena": ["neutral", "good"],
            "filipp": [],
            "ermil": ["neutral", "good"],
            "jane": ["neutral", "good", "evil"],
            "madi_ru": [],
            "saule_ru": [],
            "omazh": ["neutral", "evil"],
            "zahar": ["neutral", "good"],
            "dasha": ["neutral", "good", "friendly"],
            "julia": ["neutral", "strict"],
            "lera": ["neutral", "friendly"],
            "masha": ["good", "strict", "friendly"],
            "marina": ["neutral", "whisper", "friendly"],
            "alexander": ["neutral", "good"],
            "kirill": ["neutral", "strict", "good"],
            "anton": ["neutral", "good"]
        }

    @property
    def voice(self):
        with self._lock:
            return self._voice

    @voice.setter
    def voice(self, new_voice: str):
        with self._lock:
            self._voice = new_voice

    @property
    def role(self):
        with self._lock:
            return self._role

    @role.setter
    def role(self, new_role: str):
        with self._lock:
            self._role = new_role

    @property
    def volume(self):
        with self._lock:
            return self._volume

    @volume.setter
    def volume(self, new_volume: int):
        with self._lock:
            self._volume = new_volume

    @property
    def host(self):
        with self._lock:
            return self._host

    @host.setter
    def host(self, new_host: str):
        with self._lock:
            self._host = new_host

    @property
    def voices(self):
        with self._lock:
            return self._voices
