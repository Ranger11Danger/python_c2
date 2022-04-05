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