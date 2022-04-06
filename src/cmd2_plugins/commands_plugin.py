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
        msg = self.encrypt_msg(json.dumps(payload), self.aes_secret)
        print(len(msg))
        self.connection['socket'].send(str(len(msg)).encode())
        self.connection['socket'].send(msg)
        response_len = self.connection['socket'].recv(8)
        response = self.connection['socket'].recv(int(response_len.decode()))
        msg = self.decrypt_msg(response, self.aes_secret)
        print(msg.decode())