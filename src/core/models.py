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
import binascii


class BitcoinWallet:
    def __init__(self):
        super().__init__()

    #-------------using eth_keys, os library-------------
    def generate_private_key(self):
        # Generate the private + public key pair (using the secp256k1 curve)
        signerPrivKey = eth_keys.keys.PrivateKey(os.urandom(32))
        return signerPrivKey

    def generate_public_key(self, private_key):
        return (private_key.public_key)

    '''
    recover private key from string
    @params: string privateKey
    @return PrivateKey object
    @author HieuLe
    '''
    def recover_private_key(self, privateKey):
        byteHexPriv = privateKey.encode()
        bytePriv = binascii.unhexlify(byteHexPriv)
        priv = eth_keys.keys.PrivateKey(bytePriv)
        return priv

    #-------------end using eth_keys, os library-------------

class Blockchain:
    def __init__(self):
        super().__init__()

    # def createGenesisBlock(self):
    #     GenesisBlock = Block(0, "0", 1465154705, "my genesis block!!", "816534932c2b7154836da6afc367695e6337db8a921823784c14378abed4f7d7", 0)
    #     self.chain.append(GenesisBlock)

    # def getLatestBlock(self):
    #     return self.chain[-1]

    def getLatestBlock(self):
        db_ = MySQLdb.connect(host="localhost", port=3306, user="root", passwd="",db="blockchain")
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

    '''
    get all un spend trans_output by signature
    @param eth_object signature
    @param String msg
    '''
    def get_by_signature(self, signature, msg):
        publicKey = signature.recover_public_key_from_msg(msg)
        db_ = MySQLdb.connect(
            host="localhost", 
            port=3306, 
            user="root", 
            passwd="", 
            db="blockchain")
        db_cursor = db_.cursor()
        sql = "SELECT * FROM trans_output WHERE public_key ="
        sql += publicKey[2:].encode()
        db_cursor.execute(sql)
        result = db_cursor.fetchall()

