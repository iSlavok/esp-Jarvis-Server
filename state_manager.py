from threading import Lock


class StateManager:
    def __init__(self, initial_state: str):
        self._state = initial_state
        self._lock = Lock()
        self.states = ["waiting", "recording", "responding", "speaking", "button_recording"]

    @property
    def state(self):
        with self._lock:
            return self._state

    @state.setter
    def state(self, new_state: str):
        with self._lock:
            if new_state in self.states:
                self._state = new_state
            else:
                raise ValueError(f"Invalid state: {new_state}")