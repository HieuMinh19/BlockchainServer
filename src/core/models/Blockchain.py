from Block import Block
import time
import json
from hashlib import sha256

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

    def getLatestBlock(self):
        #print(len(self.chain)) 
        return self.chain[-1]

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
        while not computed_hash.startswith('0' * self.difficulty):
            nonce += 1
            computed_hash = self.calculateHash(index, previousHash, timestamp, data, nonce)

        return Block(index, previousHash, timestamp, data, computed_hash, nonce)

    def display_chain(self):
        for block in self.chain:
            print("index: " + str(block.index))
            print("Transaction " + block.transaction)