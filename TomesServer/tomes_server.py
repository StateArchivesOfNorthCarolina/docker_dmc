import socketserver
import json
import subprocess

class TomesTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        json_obj = json.loads(self.data.decode("utf-8"))
        json_obj_handle = JsonObjHandler(json_obj)
        t = json_obj_handle.msg.encode('utf-8')
        self.request.sendall(t)


class JsonObjHandler:
    def __init__(self, data):
        self.READPST = 0
        self.CMDDARCMAIL = 1
        self.TAGGER = 2
        """
        :type data: dict
        :param data:
        """
        if data is not None:
            for k, v in data.items():
                if k == '0':
                    self.readpst = HandleReadPST(v)
                    self.msg = "Success"
                    continue
                if k == '1':
                    self.handle_darcmail = HandleDarcMailCLI(v)
                    self.msg = "Success"
                    continue
                if k == '2':
                    self.msg = "Not Implemented"
                    pass


class HandleReadPST:
    def __init__(self, data):
        self.data = data
        self.account_name = data["account_name"]
        self.target_file = data["target_file"]
        subprocess.run(["readpst", "-o", self.account_name, self.target_file], stdout=subprocess.PIPE)
        print(self.data)


class HandleDarcMailCLI:
    def __init__(self, data):
        self.data = data
        print(self.data)

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 57775
    server = socketserver.TCPServer((HOST, PORT), TomesTCPHandler)
    server.serve_forever()