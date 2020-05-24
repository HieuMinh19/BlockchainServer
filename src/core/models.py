from django.db import models
import time
import random
import secrets

import time
import random
import secrets
import codecs
import hashlib
import ecdsa


class KeyGenerator:
    def __init__(self):
        self.POOL_SIZE = 256
        self.KEY_BYTES = 32
        # n = 1.158 x 10^17
        self.CURVE_ORDER = int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141', 16)
        self.pool = [0] * self.POOL_SIZE
        self.pool_pointer = 0
        self.prng_state = None
        self.__init_pool()
        self.string = ''
        
    def seed_input(self, str_input):
        time_int = int(time.time())
        self.__seed_int(time_int)
        """
        vòng for dưới đây mang ý nghĩa:
        đưa 1 chuỗi các bit ngẫu nhiên vào một hàm băm SHA256
        -> tạo ra một số 256 bit.
        """
        for char in str_input:
            char_code = ord(char)  
            self.__seed_byte(char_code)
            
    def generate_key(self):
        big_int = self.__generate_big_int()
        big_int = big_int % (self.CURVE_ORDER - 1) # key < curve order
        big_int = big_int + 1 # key > 0
        key = hex(big_int)[2:]
        # Add leading zeros if the hex key is smaller than 64 chars
        key = key.zfill(self.KEY_BYTES * 2)
        return key

    def __init_pool(self):
        for i in range(self.POOL_SIZE):
            random_byte = secrets.randbits(8)
            self.__seed_byte(random_byte)
        time_int = int(time.time())
        self.__seed_int(time_int)

    def __seed_int(self, n):
        self.__seed_byte(n)
        self.__seed_byte(n >> 8)            #comback 8 bit    
        self.__seed_byte(n >> 16)
        self.__seed_byte(n >> 24)

    def __seed_byte(self, n):
        self.pool[self.pool_pointer] ^= n & 255  # & => Sets each bit to 1 if both bits are 1
        self.pool_pointer += 1
        if self.pool_pointer >= self.POOL_SIZE:
            self.pool_pointer = 0
    
    def __generate_big_int(self):
        if self.prng_state is None:
            seed = int.from_bytes(self.pool, byteorder='big', signed=False)
            random.seed(seed)
            self.prng_state = random.getstate()
        random.setstate(self.prng_state)
        big_int = random.getrandbits(self.KEY_BYTES * 8)
        self.prng_state = random.getstate()
        return big_int

class BitcoinWallet:
    def __init__(self):
        super().__init__()

    def private_to_public(self, private_key):
        private_key_bytes = codecs.decode(private_key, 'hex')
        # Get ECDSA public key
        key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
        key_bytes = key.to_string()
        key_hex = codecs.encode(key_bytes, 'hex')
        # Add bitcoin byte
        bitcoin_byte = b'04'
        public_key = bitcoin_byte + key_hex
        return public_key
