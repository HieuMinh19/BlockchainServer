class UnspentTransactionOutput:
    def __init__(self, block_hash, index):
        """
        block_hash: hashData of block has transaction unspent
        index: index of v_out in transaction
        """
        self.block_hash = block_hash
        self.index = index
