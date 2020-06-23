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
    
    '''
    get largest un spend trans_output by signature
    @param eth_object signature
    @param String msg
    @param integer amount
    @return TransactionOutput object or NULL
    '''
    def get_output_by_sign(self, signature, msg, amount):
        publicKey = signature.recover_public_key_from_msg(msg)
        strPublicKey = str(publicKey)[2:]
        db_ = MySQLdb.connect(
            host="localhost", 
            port=3306, 
            user="root", 
            passwd="", 
            db="blockchain")
        db_cursor = db_.cursor()
        sql = 'SELECT * FROM trans_output WHERE public_key = '
        sql += '"'
        sql += strPublicKey
        sql += '"'
        sql +=  " AND amount > "
        sql += str(amount)
        sql += " LIMIT 1"
        db_cursor.execute(sql)
        result = db_cursor.fetchall()
        if(db_cursor.rowcount):    
            for row in result:
                #id = row[0]
                totalAmount = row[1]
                txIndex = row[2]
                publicKey = row[3]
                blockHash = row[4]

            transOutput = TransactionOutput(totalAmount, txIndex, publicKey, blockHash)
            return transOutput
        else: 
            return None

    '''
    create array transaction output and return uspend amount
    @param: transOutput TransactionOutput Object
    @param: float -> cost: total amount using
    @param: String -> publicKey
    @param: String ->blockHash
    @return: Object -> TransactionOutput
    '''
    def calculate_trans_output(self, transOutput, cost, publicKey, blockHash):
        result = []
        returnCost = transOutput.amount - cost
        transOutput = TransactionOutput(cost, 0, publicKey, blockHash)
        returnTransOutput = TransactionOutput(returnCost, 1, publicKey, blockHash)
        result.append(transOutput)
        result.append(returnTransOutput)

        return result

class TransactionInput:
    def __init__(self, tx_hash, tx_index, script_sig, block_hash):
        """
        tx_hash: ID giao dịch dùng để chi tiêu
        tx_index: index của output trong array
        script_sig: chữ kí chứng nhận quyền sở hữu
        sequence: được dùng cho thời gian hóa hoặc bị vô hiệu hóa
        (A Unix timestamp or block number) -> có thể sẽ bỏ trường này. 
        block_hash: block chứa trans input
        """
        self.tx_hash = tx_hash
        self.tx_index = tx_index
        self.script_sig = script_sig
        self.block_hash = block_hash
        #self.sequence = sequence

    def insert_to_db(self):
        db_ = MySQLdb.connect(
            host="localhost", 
            port=3306, 
            user="root", 
            passwd="",
            db="blockchain")
        db_cursor = db_.cursor()
        sql = "INSERT INTO trans_output (tx_hash, tx_index, strip_sign, block_hash) VALUE "
        sql += "('%s', '%s', '%s', '%s')" % (
            self.tx_hash,
            self.tx_index,
            self.script_sig,
            self.block_hash
        )
        db_cursor.execute(sql)    

class TransactionOutput:
    def __init__(self, amount, tx_index, public_key_from, block_hash, public_key_to):
        """
        value: giá trị cổ phiếu giao dịch
        tx_index: index của transaction trong mảng
        script_sign: kịch bản khóa.
        """
        self.amount = amount
        self.tx_index = tx_index
        self.public_key_to = public_key_to
        self.block_hash = block_hash
        self.public_key_from = public_key_from

    def insert_to_db(self):
        db_ = MySQLdb.connect(
            host="localhost", 
            port=3306, 
            user="root", 
            passwd="",
            db="blockchain")
        db_cursor = db_.cursor()
        sql = "INSERT INTO trans_output (amount, tx_index, public_key_from, block_hash, public_key_to) VALUE "
        sql += "('%s', '%s', '%s', '%s', '%s')" % (
            self.amount,
            self.tx_index,
            self.public_key_from,
            self.block_hash,
            self.public_key_to
        )
        db_cursor.execute(sql)        
    

class GlobalFunction:    
    '''
    create array transaction output and return uspend amount
    @param: transOutput TransactionOutput Object
    @param: float -> cost: total amount using
    @param: String -> receiveUser: public Key receive user
    @param: String -> selfHash: public Key your self
    @param: String ->blockHash
    @return: Array Object -> TransactionOutput
    '''
    def calculate_trans_output(self, transOutput, cost, receiveUser, selfHash, blockHash):
        result = []
        returnCost = transOutput.amount - cost
        transOutput = TransactionOutput(cost, 0, selfHash, blockHash, receiveUser) # tx_index = 0
        returnTransOutput = TransactionOutput(returnCost, 1, selfHash, blockHash, selfHash) #tx_index = 1
        result.append(transOutput)
        result.append(returnTransOutput)

        return result

    '''
    check trans_out has been used?
    @param: Integer txIndex,
    @param:  String blockHash
    @return boolean
    '''
    def is_using_trans_output(self, txIndex, blockHash):
        db_ = MySQLdb.connect(
            host="localhost", 
            port=3306, 
            user="root", 
            passwd="", 
            db="blockchain")
        db_cursor = db_.cursor()
        sql = 'SELECT * FROM trans_input WHERE tx_index = ' 
        sql += '"' + str(txIndex) + '"'
        sql += ' AND tx_hash = ' +  '"' + str(blockHash) + '"'
        sql += " LIMIT 1"
        print(sql)
        db_cursor.execute(sql)

        if(db_cursor.rowcount):
            return True
        
        return False

    '''
    get available transaction output
    @params: Integer amount
    @params: Array Object arrTransOutput
    @return Array  
    '''
    def available_trans_output(self, amount, arrTransOutput):
        arrResult = []
        globalFunc = GlobalFunction()        
        
        # init value
        index = 0
        totalAmount = arrTransOutput[index].amount
        arrResult.append(arrResult[index])        
        while(totalAmount <= amount):
            txIndex = arrTransOutput[index].tx_index
            blockHash = arrTransOutput[index].block_hash
            if(globalFunc.is_using_trans_output(txIndex, blockHash) == False):
                index += 1
                totalAmount += arrTransOutput[index].amount
                arrResult.append(arrResult[index])

        return arrResult

    '''
    get all transaction output from DB (used and un-use)
    @parmas: signature Object
    @params: msg String
    @params: amount Integer
    @return: Array Transaction output
    '''
    def get_trans_output_by_sign(self, signature, msg, amount):
        arrTransOutput = []
        publicKey = signature.recover_public_key_from_msg(msg)
        strPublicKey = str(publicKey)[2:]
        db_ = MySQLdb.connect(
            host="localhost", 
            port=3306, 
            user="root", 
            passwd="", 
            db="blockchain")
        db_cursor = db_.cursor()
        sql = 'SELECT * FROM trans_output WHERE public_key = '
        sql += '"'
        sql += strPublicKey
        sql += '"'
        db_cursor.execute(sql)
        result = db_cursor.fetchall()
        if(db_cursor.rowcount):    
            for row in result:
                #id = row[0]
                totalAmount = row[1]
                txIndex = row[2]
                publicKeyFrom = row[3]
                blockHash = row[4]
                publicKeyTo = row[5]
                transOutput = TransactionOutput(totalAmount, txIndex, publicKeyFrom, blockHash, publicKeyTo)
                arrTransOutput.append(transOutput)

        return arrTransOutput

