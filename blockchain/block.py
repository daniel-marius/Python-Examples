from printable import Printable


class Block(Printable):

    def __init__(self, block_header='', transactions=''):
        self.block_header = block_header
        self.transactions = transactions
