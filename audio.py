import socket
import struct
import wave


class Audio:
    def __init__(self, ip: str, port: int, gain: int, chunk_size: int, sample_rate: int, callback):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.gain = gain
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.callback = callback
        self.enable = True
        self.enable_write = False
        self.wav_file = None
        self.file_num = 0

    def streaming_from_udp(self):
        try:
            while True:
                if self.enable:
                    data, _ = self.sock.recvfrom(self.chunk_size * 2)
                    audio_data = struct.unpack('<' + 'h' * (len(data) // 2), data)
                    amplified_data = [int(sample * self.gain) for sample in audio_data]
                    amplified_data = [max(-32768, min(32767, sample)) for sample in amplified_data]
                    if self.enable_write and self.wav_file is not None:
                        audio_data = struct.pack('<' + 'h' * len(amplified_data), *amplified_data)
                        self.wav_file.writeframes(audio_data)
                    self.callback(amplified_data)
        except Exception as e:
            print(f"Error audio: {e}")
        finally:
            self.sock.close()

    def new_file(self) -> bool:
        if self.wav_file is not None:
            return False
        self.file_num += 1
        self.wav_file = wave.open(f"audio/{self.file_num}.wav", 'wb')
        self.wav_file.setnchannels(1)
        self.wav_file.setsampwidth(2)
        self.wav_file.setframerate(self.sample_rate)
        return True

    def close_file(self):
        if self.wav_file is None:
            return False
        self.wav_file.close()
        self.wav_file = None
        return True
