import socketserver


class TomesTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("{} wrote: ".format(self.client_address[0]))
        print(self.data)
        self.request.sendall(self.data.upper())


if __name__ == "__main__":
    HOST, PORT = "localhost", 57775
    server = socketserver.TCPServer((HOST, PORT), TomesTCPHandler)
    server.serve_forever()