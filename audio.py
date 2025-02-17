import os
import socket


class Audio:
    def __init__(self, ip: str, port: int, ffmpeg_proc):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.ffmpeg_proc = ffmpeg_proc
        self.enable_write = False
        self.file_num = 0

    def streaming_from_udp(self):
        try:
            while True:
                data, _ = self.sock.recvfrom(4096)
                self.ffmpeg_proc.stdin.write(data)
                self.ffmpeg_proc.stdin.flush()
                if self.enable_write:
                    with open(f"audio/{self.file_num}.mp3", 'ab') as f:
                        f.write(data)
        except Exception as e:
            print(f"Error audio: {e}")
        finally:
            self.sock.close()

    def new_file(self):
        self.file_num += 1
        if os.path.exists(f"audio/{self.file_num}.mp3"):
            os.remove(f"audio/{self.file_num}.mp3")
        self.enable_write = True

    def close_file(self):
        self.enable_write = False
