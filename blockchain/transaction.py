from Crypto.Hash import SHA3_256


class Transaction:

    def __init__(self, sender=None, recipient=None, coins=0.00, fees=0.00, relay_fees=0.00, signature=None):
        self.sender = sender
        self.recipient = recipient
        self.coins = coins
        self.fees = fees
        self.relay_fees = relay_fees
        self.signature = signature
        self.transaction_id = self.transaction_hash()

    def transaction_hash(self):
        transaction_string = (str(self.sender) +
                              str(self.recipient) +
                              str(self.coins) +
                              str(self.fees) +
                              str(self.relay_fees) +
                              str(self.signature)).encode()
        h = SHA3_256.new(transaction_string)
        return h.hexdigest()
