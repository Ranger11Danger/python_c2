from base64 import decode
import json
from rich.table import Table
import time
from cmd2 import Cmd2ArgumentParser, with_argparser

select_parser = Cmd2ArgumentParser()
select_parser.add_argument("id", help = "Client ID to interact with")

class Plugin:
    def do_get_clients(self, args):
        msg = self.encrypt_msg("get_clients", self.aes_secret)
        self.connection['socket'].send(("0"*(8 - len(str(len(msg))))+str(len(msg))).encode() + msg)
        data_len = self.connection['socket'].recv(8)
        data = self.connection['socket'].recv(int(data_len.decode()))
        data = self.decrypt_msg(data, self.aes_secret)
        data = json.loads(data.decode())
        table = Table("Client ID", "Hostname", "Remote IP", "Remote Port", "Connection Time", title="Connected Clients")
        for key, val in data.items():
            if key not in self.clients:
                self.clients[key] = val
            table.add_row(str(key),str(val["info"]["hostname"]) ,str(val["connection"][0]), str(val["connection"][1]), f'{str(val["info"]["date"])} {str(val["info"]["time"])}')
        self.console.print(table)

    @with_argparser(select_parser)
    def do_select(self, args):
        self.client = args.id
        self.prompt = f"({self.clients[args.id]['info']['hostname']}): "

    def do_back(self, args):
        self.client = None
        self.prompt = "(Connected)"