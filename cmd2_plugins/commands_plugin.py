import json

class Plugin:
    def do_test(self, args):
        self.send_command("test")

    def do_info(self, args):
        self.send_command("lsb_release")

    def do_ps(self, args):
        self.send_command("ps")

    def send_command(self, command):
        payload = {
            "client_id" : self.client,
            "command" : command
        }
        self.connection['socket'].send(json.dumps(payload).encode())
        response = self.connection['socket'].recv(50000)
        print(response.decode())