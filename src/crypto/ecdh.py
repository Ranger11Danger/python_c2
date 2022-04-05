import hashlib
import random
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
        return hashlib.sha256(str(full_key).encode()).hexdigest()[:32]