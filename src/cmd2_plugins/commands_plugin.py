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
        self.connection['socket'].send(msg)
        response = self.connection['socket'].recv(50000)
        msg = self.decrypt_msg(response, self.aes_secret)
        print(msg.decode())