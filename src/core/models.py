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
import eth_keys, os
import MySQLdb
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

    def generate_address(self, private_key):
        public_key = BitcoinWallet.private_to_public(self, private_key)
        address = BitcoinWallet.public_to_address(self, public_key)
        return address
    
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

    def public_to_address(self, public_key):
        public_key_bytes = codecs.decode(public_key, 'hex')
        # Run SHA256 for the public key
        sha256_bpk = hashlib.sha256(public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()     #tranfer to byte type
        # Run ripemd160 for the SHA256
        ripemd160_bpk = hashlib.new('ripemd160')
        ripemd160_bpk.update(sha256_bpk_digest)
        ripemd160_bpk_digest = ripemd160_bpk.digest()
        ripemd160_bpk_hex = codecs.encode(ripemd160_bpk_digest, 'hex')
        # Add network byte
        network_byte = b'00'
        network_bitcoin_public_key = network_byte + ripemd160_bpk_hex
        network_bitcoin_public_key_bytes = codecs.decode(network_bitcoin_public_key, 'hex')
        # Double SHA256 to get checksum
        sha256_nbpk = hashlib.sha256(network_bitcoin_public_key_bytes)
        sha256_nbpk_digest = sha256_nbpk.digest()
        sha256_2_nbpk = hashlib.sha256(sha256_nbpk_digest)
        sha256_2_nbpk_digest = sha256_2_nbpk.digest()
        sha256_2_hex = codecs.encode(sha256_2_nbpk_digest, 'hex')
        checksum = sha256_2_hex[:8]
        # Concatenate public key and checksum to get the address
        address_hex = (network_bitcoin_public_key + checksum).decode('utf-8')
        wallet = BitcoinWallet.base58(self, address_hex)
        return wallet

    def base58(self, address_hex):
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        b58_string = ''
        # Get the number of leading zeros and convert hex to decimal
        leading_zeros = len(address_hex) - len(address_hex.lstrip('0'))
        # Convert hex to decimal
        address_int = int(address_hex, 16)
        # Append digits to the start of string
        while address_int > 0:
            digit = address_int % 58
            digit_char = alphabet[digit]
            b58_string = digit_char + b58_string
            address_int //= 58
        # Add '1' for each 2 leading zeros
        ones = leading_zeros // 2
        for one in range(ones):
            b58_string = '1' + b58_string
        return b58_string

    #-------------using eth_keys, os library-------------
    def generate_private_key(self):
        # Generate the private + public key pair (using the secp256k1 curve)
        signerPrivKey = eth_keys.keys.PrivateKey(os.urandom(32))
        return signerPrivKey

    def generate_public_key(self, private_key):
        return (private_key.public_key)

    def generate_signature(self, private_key, msg):
        private = eth_keys.keys.PrivateKey(private_key)
        print(private)        
        signature = private.sign_msg(msg)
        return signature
    #-------------end using eth_keys, os library-------------

class Blockchain:
    difficulty = 2
    def __init__(self):
        """
        Constructor của class `Blockchain`.
        """
        self.chain = [] 
        self.createGenesisBlock()

    def createGenesisBlock(self):
        GenesisBlock = Block(0, "0", 1465154705, "my genesis block!!", "816534932c2b7154836da6afc367695e6337db8a921823784c14378abed4f7d7", 0)
        self.chain.append(GenesisBlock)

    # def getLatestBlock(self):
    #     return self.chain[-1]

    def getLatestBlock(self):
        db_ = MySQLdb.connect(host="localhost", port=3306, user="root", passwd="",db="blockchain")
        db_.autocommit(True)
        db_cursor = db_.cursor()
        sql = "SELECT * FROM blocks ORDER by id DESC limit 1"
        db_cursor.execute(sql)
        result = db_cursor.fetchall()
        db_.commit() 

        for row in result:
            index = row[0]
            previousHash = row[1]
            timestamp = row[2]
            transaction = row[3]
            hashData = row[4]
            nonce = row[5]
        
        return Block(index, previousHash, timestamp, transaction, hashData, nonce)

    def calculateHash(self, index, previousHash, timestamp, data, nonce):
        data = (str(index) + previousHash + 
        str(timestamp) + data + str(nonce)).encode('utf-8')
        
        return sha256(data).hexdigest()

    def generateNextBlock(self, blockData):
        prevBlock = self.getLatestBlock()
        nextIndex = prevBlock.index + 1
        timestamp = int(time.time()) 
        #nextHash = self.calculateHash(nextIndex, prevBlock.hashData, timestamp, blockData)
        #nextHash = 
        return self.proof_of_work(nextIndex, prevBlock.hashData, timestamp, blockData, nonce=0)

    def proof_of_work(self, index, previousHash, timestamp, data, nonce):
        """
        Hàm thử các giá trị khác nhau của nonce để lấy giá trị băm thỏa mãn
        """
        nonce = 0 
        computed_hash = self.calculateHash(index, previousHash, timestamp, data, nonce)
        while not computed_hash.startswith('0' * self.get_difficulty):
            nonce += 1
            computed_hash = self.calculateHash(index, previousHash, timestamp, data, nonce)

        return Block(index, previousHash, timestamp, data, computed_hash, nonce)

    def display_chain(self):
        for block in self.chain:
            print("index: " + str(block.index))
            print("Transaction " + block.transaction)

    def get_difficulty(self):
        db_ = MySQLdb.connect(
            host="localhost", 
            port=3306, 
            user="root", 
            passwd="",
            db="blockchain")
        db_.autocommit(True)
        db_cursor = db_.cursor()
        sql = "SELECT difficult FROM configs limit 1"
        db_cursor.execute(sql)
        result = db_cursor.fetchall()
        db_.commit() 
        for row in result:
            difficult = row[0]
        
        return difficult

class Block:
    # index = models.IntegerField()
    # previousHash = models.CharField(max_length=255)
    # timestamp = models.IntegerField()
    # transaction = models.TextField()
    # hashData = models.CharField(("hash of Block"), max_length=255)
    # nonce = models.IntegerField()

    def __init__(self, index, previousHash, timestamp, transaction, hashData, nonce):
        """
        Constructor cho một `Block` class.
        :param index: Chỉ số ID duy nhất của một block.
        :param previousHash: Chỉ số khối trước đó.
        :param timestamp: Thời gian tạo block.(unix timestamp)
        :param transaction: list v_in và v_out dạng json
        :param hashdata: hash của block
        :param nonce: hằng số nonce của riêng block
        """
        self.index = index
        self.previousHash = previousHash
        self.timestamp = timestamp
        self.transaction = transaction
        self.hashData = hashData
        self.nonce = nonce

    def calculateHashForBlock(self):
        data = (str(self.index) + self.previousHash + 
        str(self.timestamp) + self.transaction + str(self.nonce)).encode('utf-8')
        self.hashData = sha256(data).hexdigest()
        return self.hashData

class TransactionInput:
    def __init__(self, tx_hash, tx_index, script_sig):
        """
        tx_hash: ID giao dịch dùng để chi tiêu
        tx_index: index của output trong array
        script_sig: chữ kí chứng nhận quyền sở hữu
        sequence: được dùng cho thời gian hóa hoặc bị vô hiệu hóa
        (A Unix timestamp or block number) -> có thể sẽ bỏ trường này. 
        """
        self.tx_hash = tx_hash
        self.tx_index = tx_index
        self.script_sig = script_sig
        #self.sequence = sequence

class TransactionOutput:
    def __init__(self, value, tx_index, script_sig):
        """
        value: giá trị cổ phiếu giao dịch
        tx_index: index của transaction trong mảng
        script_sign: kịch bản khóa.
        """
        self.value = value
        self.tx_index = tx_index
        self.script_sign = script_sig


