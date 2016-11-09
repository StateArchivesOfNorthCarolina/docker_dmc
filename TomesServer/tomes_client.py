import socket
import sys


class TomesClient:

    def __init__(self):
        self.received = None
        self.sent = None
        self.HOST = "127.0.0.1"
        self.PORT = 57775

    def send_package(self, data):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.HOST, self.PORT))
            sock.sendall(bytes(data, "utf-8"))
            self.received = str(sock.recv(1024))
