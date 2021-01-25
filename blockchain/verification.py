from ecc_wallet import Wallet
from merkle_tree import MerkleTree


class Verification:

    @staticmethod
    def verify_blockchain(blockchain, difficulty, proof_of_work):
        local_blockchain = blockchain.copy()
        mt = MerkleTree()
        for i in range(1, len(local_blockchain)):
            current_block_header = local_blockchain[i].__dict__['block_header']
            previous_block_header = local_blockchain[i - 1].__dict__['block_header']

            get_transactions = [[transaction['transaction_id'] for transaction in block.transactions] for block in
                                local_blockchain]

            # print('transaction_id for block {} : {}'.format(i, get_transactions[i]))
            # print('merkle tree root for block {} : {}'.format(i, mt.merkle_tree_construct(get_transactions[i])))

            recomputed_merkle_tree_root = mt.merkle_tree_construct(get_transactions[i])

            if not proof_of_work(previous_block_header):
                return False

            [current_block_header_nonce_recomputed,
             current_block_header_hash_recomputed,
             current_block_header_hash_rate_recomputed] = proof_of_work(previous_block_header)

            if current_block_header['pow_hash'] != current_block_header_hash_recomputed:
                return False

            if current_block_header['prev_block_hash'] != previous_block_header['pow_hash']:
                return False

            if current_block_header['merkle_tree_root'] != recomputed_merkle_tree_root:
                return False

            if current_block_header['index'] != previous_block_header['index'] + 1:
                return False

            if current_block_header['nonce'] != current_block_header_nonce_recomputed:
                return False

            if current_block_header['difficulty'] != difficulty:
                return False

        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.__dict__['coins'] > transaction.__dict__['fees'] >= 0 and \
                   sender_balance >= transaction.__dict__['coins'] > transaction.__dict__['relay_fees'] >= 0 and \
                   Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactions(cls, pending_transactions, get_balance):
        return all([cls.verify_transaction(tx, get_balance, False) for tx in pending_transactions])
