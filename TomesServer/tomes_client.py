import json
import socket
import sys

HOST, PORT = "192.168.99.100", 57775

data = "Hello, World!"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall(bytes(json.dumps(data), "utf-8"))
    rec = str(sock.recv(1024))

print("Sent:        {}".format(data))
print("Received:    {}".format(rec))
