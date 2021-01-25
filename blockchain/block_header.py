from time import time

from Crypto.Hash import SHA3_256


class BlockHeader:

    def __init__(self, version=1.0, block_id='', prev_block_hash='', pow_hash='', merkle_tree_root='', beneficiary='',
                 difficulty=0, index=0, nonce=0, hash_rate='', timestamp=None):
        self.version = version
        self.block_id = block_id
        self.prev_block_hash = prev_block_hash
        self.pow_hash = pow_hash
        self.merkle_tree_root = merkle_tree_root
        self.beneficiary = beneficiary
        self.difficulty = difficulty
        self.index = index
        self.nonce = nonce
        self.hash_rate = hash_rate
        self.timestamp = time() if timestamp is None else timestamp

    def block_header_hash(self):
        block_header_string = (str(self.version) +
                               str(self.block_id) +
                               str(self.prev_block_hash) +
                               str(self.pow_hash) +
                               str(self.merkle_tree_root) +
                               str(self.beneficiary) +
                               str(self.difficulty) +
                               str(self.index) +
                               str(self.nonce) +
                               str(self.hash_rate))
        h = SHA3_256.new(block_header_string.encode())
        return h.hexdigest()
