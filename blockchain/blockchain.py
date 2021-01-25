import base64
import functools
import json
import os
import time
import uuid

import requests
from Crypto.Hash import SHA256, SHA3_256, HMAC
from block import Block
from block_header import BlockHeader
from ecc_wallet import Wallet
from memory_pool import Mempool
from merkle_tree import MerkleTree
from transaction import Transaction
from utility import Utility
from verification import Verification

BOOTSTRAP_LIST = ["localhost:5000", "localhost:5001", "localhost:5002", "localhost:5003", "localhost:5004"]
DEFAULT_DIFFICULTY = 1
MINING_REWARD = 10


class Blockchain:

    def __init__(self, hosting_address, node_id):
        self.__genesis_block_header = BlockHeader()
        self.__genesis_block_header.pow_hash = self.__genesis_block_header.block_header_hash()
        self.__genesis_block = Block(self.__genesis_block_header.__dict__, [])
        self.__blockchain = [self.__genesis_block]
        self.__pending_transactions = []
        self.__hosting_address = hosting_address
        self.__peer_nodes = set()
        self.__node_id = node_id
        self.__resolve_conflicts = False
        self.load_blockchain()
        self.__merkle_tree = MerkleTree()
        self.__mempool = Mempool()
        self.__rand_values = []
        self.__difficulty = DEFAULT_DIFFICULTY
        self.load_difficulty()

    def __len__(self):
        """ Returns the length of the chain """
        return len(self.__blockchain)

    @property
    def hosting_address(self):
        return self.__hosting_address

    @hosting_address.setter
    def hosting_address(self, hosting_address):
        self.__hosting_address = hosting_address

    @property
    def node_id(self):
        return self.__node_id

    @node_id.setter
    def node_id(self, node_id):
        self.__node_id = node_id

    @property
    def resolve_conflicts(self):
        return self.__resolve_conflicts

    @resolve_conflicts.setter
    def resolve_conflicts(self, resolve_conflicts):
        self.__resolve_conflicts = resolve_conflicts

    @property
    def difficulty(self):
        return self.__difficulty

    @difficulty.setter
    def difficulty(self, difficulty):
        self.__difficulty = difficulty

    @property
    def blockchain(self):
        return self.__blockchain[:]

    @blockchain.setter
    def blockchain(self, blockchain):
        self.__blockchain = blockchain

    @property
    def pending_transactions(self):
        return self.__pending_transactions[:]

    @pending_transactions.setter
    def pending_transactions(self, pending_transactions):
        self.__pending_transactions = pending_transactions

    @property
    def rand_values(self):
        return self.__rand_values[:]

    @rand_values.setter
    def rand_values(self, rand_values):
        self.__rand_values = rand_values

    def get_first_block_header(self):
        """ Returns the first block header of the blockchain """
        if self.__blockchain.__len__() < 1:
            return None
        return self.__blockchain[0].__dict__['block_header']

    def get_last_block_header(self):
        """ Returns the last block header of the blockchain """
        if self.__blockchain.__len__() < 1:
            return None
        return self.__blockchain[-1].__dict__['block_header']

    def get_parent_block_prev_hash(self, block):
        if block['block_header']['index'] == self.__genesis_block_header.index:
            return None

        get_index = block['block_header']['index'] - 1
        if block['block_header']['index'] > 1 and get_index != 0 and \
                self.__blockchain[get_index].__dict__['block_header']['prev_block_hash'] != '':
            return self.__blockchain[get_index].__dict__['block_header']['prev_block_hash']

    def get_child_block_prev_hash(self, block):
        if block['block_header']['index'] == self.__genesis_block_header.index:
            return None

        if block['block_header']['index'] == self.__blockchain.__len__() - 1:
            return None

        if block['block_header']['index'] + 1 != 0:
            get_index = block['block_header']['index'] + 1
            return self.__blockchain[get_index].__dict__['block_header']['prev_block_hash']

    def print_transactions(self):
        get_transactions = [[transaction for transaction in block.transactions] for block in self.__blockchain]
        print(get_transactions)

    def print_blockchain(self):
        """ Print the entire blockchain """
        for i in range(self.__blockchain.__len__()):
            print(self.__blockchain[i])

    @staticmethod
    def generate_hmac(secret_key, input_key):
        h = HMAC.new(secret_key, digestmod=SHA256)
        h.update(input_key)
        return h.hexdigest()

    @staticmethod
    def verify_hmac(secret_key, input_key, hmac):
        found = False
        h = HMAC.new(secret_key, digestmod=SHA256)
        h.update(input_key)
        try:
            h.hexverify(hmac)
            print("The message is authentic!")
            found = True
        except ValueError:
            print("The message or the key is wrong!")
            found = False
        return found

    def get_balance(self, sender=None):
        if sender is None:
            if self.__hosting_address is None:
                return None
            participant = self.__hosting_address
        else:
            participant = sender
        transaction_sender = [[transaction['coins'] for transaction in block.transactions
                               if transaction['sender'] == participant] for block in self.__blockchain]

        pending_transaction_sender = [transaction['coins'] for transaction in self.__pending_transactions
                                      if transaction['sender'] == participant]

        transaction_sender_fees = [[transaction['fees'] for transaction in block.transactions
                                    if transaction['sender'] == participant] for block in self.__blockchain]

        pending_transaction_sender_fees = [transaction['fees'] for transaction in self.__pending_transactions
                                           if transaction['sender'] == participant]

        transaction_sender_relay_fees = [[transaction['relay_fees'] for transaction in block.transactions if
                                          transaction['sender'] == participant] for block in self.__blockchain]

        pending_transaction_sender_relay_fees = [transaction['relay_fees'] for transaction in
                                                 self.__pending_transactions if transaction['sender'] == participant]

        transaction_sender.append(pending_transaction_sender)
        transaction_sender_fees.append(pending_transaction_sender_fees)
        transaction_sender_relay_fees.append(pending_transaction_sender_relay_fees)

        coins_sent = functools.reduce(lambda trans_sum, trans_coins: trans_sum + sum(trans_coins)
        if len(trans_coins) > 0 else trans_sum + 0, transaction_sender, 0)

        print('coins sent: ' + str(coins_sent))

        fees_sent = functools.reduce(lambda trans_sum, trans_fees: trans_sum + sum(trans_fees)
        if len(trans_fees) > 0 else trans_sum + 0, transaction_sender_fees, 0)

        print('fees sent: ' + str(fees_sent))

        relay_fees_sent = functools.reduce(lambda trans_sum, trans_relay_fees: trans_sum + sum(trans_relay_fees)
        if len(trans_relay_fees) > 0 else trans_sum + 0,
                                           transaction_sender_relay_fees, 0)

        print('relay_fees_sent: ' + str(coins_sent))

        # coins_sent = 0
        # for tx in transaction_sender:
        # if len(tx) > 0:
        # coins_sent += tx[0]

        transaction_recipient = [[transaction['coins'] for transaction in block.transactions
                                  if transaction['recipient'] == participant] for block in self.__blockchain]

        print(transaction_recipient)

        transaction_recipient_fees = [[transaction['fees'] for transaction in block.transactions
                                       if transaction['recipient'] == participant] for block in self.__blockchain]

        print(transaction_recipient_fees)

        coins_received = functools.reduce(lambda trans_sum, trans_coins: trans_sum + sum(trans_coins)
        if len(trans_coins) > 0 else trans_sum + 0, transaction_recipient, 0)

        fees_received = functools.reduce(lambda trans_sum, trans_fees: trans_sum + sum(trans_fees)
        if len(trans_fees) > 0 else trans_sum + 0, transaction_recipient_fees, 0)

        print('coins received: ' + str(coins_received))

        print('fees received: ' + str(coins_sent))

        # coins_received = 0
        # for tx in transaction_recipient:
        # if len(tx) > 0:
        # coins_received += tx[0]

        total = coins_received + fees_received - coins_sent - fees_sent - relay_fees_sent
        print('final coins: ' + str(total))

        # return coins_received - coins_sent
        return total

    def save_difficulty(self):
        try:
            with open('difficulty.txt', mode='w') as f:
                f.write(json.dumps(self.__difficulty))
            print('Saving difficulty succeeded...')
            return True
        except (IOError, IndexError):
            print('Saving difficulty failed...')
            return False

    def save_blockchain(self):
        try:
            with open('blockchain-{}.txt'.format(self.__node_id), mode='w') as f:
                save_blockchain = [
                    block.__dict__ for block in
                    [
                        Block(block_el.block_header, block_el.transactions) for block_el in self.__blockchain
                    ]
                ]
                f.write(json.dumps(save_blockchain))
                f.write('\n')
                save_pending_transactions = [pend_tran for pend_tran in self.__pending_transactions]
                f.write(json.dumps(save_pending_transactions))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
                print('Saving blockchain succeeded...')
        except (IOError, IndexError):
            print('Saving blockchain failed...')

    def load_blockchain(self):
        try:
            with open('blockchain-{}.txt'.format(self.__node_id), mode='r') as f:
                file_content = f.readlines()
                file_chain = json.loads(file_content[0][:-1])
                file_pending_transactions = json.loads(file_content[1][:-1])
                new_blockchain = []
                for block in file_chain:
                    new_block_header = BlockHeader(block['block_header']['version'],
                                                   block['block_header']['block_id'],
                                                   block['block_header']['prev_block_hash'],
                                                   block['block_header']['pow_hash'],
                                                   block['block_header']['merkle_tree_root'],
                                                   block['block_header']['beneficiary'],
                                                   block['block_header']['difficulty'],
                                                   block['block_header']['index'],
                                                   block['block_header']['nonce'],
                                                   block['block_header']['hash_rate'],
                                                   block['block_header']['timestamp']).__dict__

                    new_transactions = [Transaction(t['sender'],
                                                    t['recipient'],
                                                    t['coins'],
                                                    t['fees'],
                                                    t['relay_fees'],
                                                    t['signature']).__dict__ for t in block['transactions']]

                    new_block = Block(new_block_header, new_transactions)
                    new_blockchain.append(new_block)
                self.__blockchain = new_blockchain
                new_pending_transactions = [Transaction(t['sender'],
                                                        t['recipient'],
                                                        t['coins'],
                                                        t['fees'],
                                                        t['relay_fees'],
                                                        t['signature']).__dict__ for t in file_pending_transactions]
                self.__pending_transactions = new_pending_transactions
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
                print('Loading blockchain file succeeded...')
        except (IOError, IndexError):
            print('Loading blockchain file failed...')

    def load_difficulty(self):
        try:
            with open('difficulty.txt', mode='r') as f:
                file_content = f.readline()
                file_difficulty = json.loads(file_content)
                self.__difficulty = int(file_difficulty)
            print('Loading difficulty file succeeded...')
        except (IOError, IndexError):
            print('Loading difficulty file failed...')

    def delete_blockchain(self):
        try:
            os.remove('blockchain-{}.txt'.format(self.__node_id))
            print('Blockchain file removed...')
        except (IOError, IndexError, SystemError):
            print('Blockchain file not found...')

    @staticmethod
    def delete_difficulty():
        try:
            os.remove('difficulty.txt')
            print('Difficulty file removed...')
        except (IOError, IndexError, SystemError):
            print('Difficulty file not found...')

    def set_new_difficulty(self, new_difficulty):
        if new_difficulty is None:
            return None

        if new_difficulty is '0':
            return None

        if int(new_difficulty) < 1:
            return None

        self.__difficulty = int(new_difficulty)
        if self.save_difficulty():
            return True
        else:
            return False

    def filter_transaction_pool(self):
        copy_pending_transactions = self.__pending_transactions[:]
        if len(copy_pending_transactions) <= 0:
            return False

        self.__pending_transactions = self.__mempool.fee_based_mempool(copy_pending_transactions)
        self.save_blockchain()

        if len(self.__pending_transactions) < 0:
            return False

        return True

    def selfish_mining(self, proof_of_work):
        if self.__hosting_address is None:
            return None

        get_last_block_header = self.get_last_block_header()
        [nonce, hash_returned, hash_rate] = proof_of_work(self.__difficulty, get_last_block_header)

        t_sender = 'System'
        t_recipient = self.__hosting_address
        t_coins = MINING_REWARD
        t_fees = 0.0
        t_relay_fees = 0.0
        t_signature = 'No Signature'

        reward_transaction = Transaction(t_sender,
                                         t_recipient,
                                         t_coins,
                                         t_fees,
                                         t_relay_fees,
                                         t_signature)

        copy_open_transactions = self.__pending_transactions[:]
        for tx in copy_open_transactions:
            if not Wallet.verify_transaction2(tx):
                return None

        copy_open_transactions.append(reward_transaction.__dict__)

        transaction_id = []
        for i in range(0, len(copy_open_transactions)):
            transaction_id.append(copy_open_transactions[i]['transaction_id'])

        software_version = 1.0
        h = SHA3_256.new(str(uuid.uuid4()).encode())
        block_header_id = h.hexdigest()
        block_header_prev_block_hash = self.get_last_block_header()['pow_hash']
        block_header_pow_hash = hash_returned
        block_header_merkle_tree_root = self.__merkle_tree.merkle_tree_construct(transaction_id)
        block_header_beneficiary = self.__hosting_address
        block_header_difficulty = self.__difficulty
        block_header_index = self.__blockchain.__len__()
        block_header_nonce = nonce
        block_header_hash_rate = hash_rate

        block_header = BlockHeader(software_version,
                                   block_header_id,
                                   block_header_prev_block_hash,
                                   block_header_pow_hash,
                                   block_header_merkle_tree_root,
                                   block_header_beneficiary,
                                   block_header_difficulty,
                                   block_header_index,
                                   block_header_nonce,
                                   block_header_hash_rate)

        block = Block(block_header.__dict__, copy_open_transactions)

        self.__blockchain.append(block)
        self.__pending_transactions = []
        self.save_blockchain()
        return block

    def mine_block(self, proof_of_work):
        if self.__hosting_address is None:
            return None

        get_last_block_header = self.get_last_block_header()
        [nonce, hash_returned, hash_rate] = proof_of_work(self.__difficulty, get_last_block_header)

        t_sender = 'System'
        t_recipient = self.__hosting_address
        t_coins = MINING_REWARD
        t_fees = 0.0
        t_relay_fees = 0.0
        t_signature = 'No Signature'

        reward_transaction = Transaction(t_sender,
                                         t_recipient,
                                         t_coins,
                                         t_fees,
                                         t_relay_fees,
                                         t_signature)

        copy_open_transactions = self.__pending_transactions[:]
        for tx in copy_open_transactions:
            if tx['signature'] == 'No Signature':
                continue
            if tx['signature'] != 'No Signature' and not Wallet.verify_transaction2(tx):
                return None

        copy_open_transactions.append(reward_transaction.__dict__)

        transaction_id = []
        for i in range(0, len(copy_open_transactions)):
            transaction_id.append(copy_open_transactions[i]['transaction_id'])

        software_version = 1.0
        h = SHA3_256.new(str(uuid.uuid4()).encode())
        block_header_id = h.hexdigest()
        block_header_prev_block_hash = self.get_last_block_header()['pow_hash']
        block_header_pow_hash = hash_returned
        block_header_merkle_tree_root = self.__merkle_tree.merkle_tree_construct(transaction_id)
        block_header_beneficiary = self.__hosting_address
        block_header_difficulty = self.__difficulty
        block_header_index = self.__blockchain.__len__()
        block_header_nonce = nonce
        block_header_hash_rate = hash_rate

        block_header = BlockHeader(software_version,
                                   block_header_id,
                                   block_header_prev_block_hash,
                                   block_header_pow_hash,
                                   block_header_merkle_tree_root,
                                   block_header_beneficiary,
                                   block_header_difficulty,
                                   block_header_index,
                                   block_header_nonce,
                                   block_header_hash_rate)

        block = Block(block_header.__dict__, copy_open_transactions)

        self.__blockchain.append(block)
        self.__pending_transactions = []
        self.save_blockchain()
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            dict_block = block.__dict__.copy()
            dict_block['transactions'] = [tx for tx in dict_block['transactions']]
            try:
                response = requests.post(url, json={'block': dict_block})
                print(url)
                print(response.content)
                if response.status_code == 400 or response.status_code == 500:
                    print('Error Block Broadcasting!')
                if response.status_code == 409:
                    self.__resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_transaction(self, sender, recipient, coins=1.0, fees=0.0, relay_fees=0.0, signature=None,
                        is_received=False):
        if self.__hosting_address is None:
            return False

        # if len(self.__pending_transactions) > 10:
        # print('Filter the Memory Pool!')
        # return False

        transaction = Transaction(sender, recipient, coins, fees, relay_fees, signature)

        # double_spending = True
        # for i in range(0, len(self.__pending_transactions)):
        # if self.__pending_transactions[i]['sender'] == transaction.sender and \
        # self.__pending_transactions[i]['coins'] == transaction.coins:
        # double_spending = False
        # print('Double Spending!')
        # break

        # if double_spending is False:
        # return False

        if Verification.verify_transaction(transaction, self.get_balance) or not \
                Verification.verify_transaction(transaction, self.get_balance):
            self.__pending_transactions.append(transaction.__dict__)
            self.save_blockchain()
            if not is_received:
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={'sender': sender,
                                                            'recipient': recipient,
                                                            'coins': coins,
                                                            'fees': fees,
                                                            'relay_fees': relay_fees,
                                                            'signature': signature})
                        print(url)
                        print(response.content)
                        if response.status_code == 400 or response.status_code == 500:
                            print('Error Transaction Broadcasting!')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def broadcast_value(self, rand_value, is_received=False):
        if str(rand_value) is None:
            return False

        if not rand_value['plainText'].isalpha():
            return None

        gen_secret_key = 'secret'
        print(rand_value['plainText'])
        print(rand_value['hmac'])

        h = HMAC.new(gen_secret_key.encode(), digestmod=SHA256).update(rand_value['plainText'].encode())
        b64 = base64.b64encode(h.digest()).decode()

        if b64 != rand_value['hmac'] and not \
                self.verify_hmac(gen_secret_key.encode(), rand_value['plainText'].encode(), h.hexdigest()):
            return None

        print(self.verify_hmac(gen_secret_key.encode(), rand_value['plainText'].encode(), h.hexdigest()))

        if rand_value['plainText'].isalpha():
            self.__rand_values.append(rand_value['plainText'])

        try:
            with open('rand_value-{}.txt'.format(self.__node_id), mode='w') as f:
                f.write(json.dumps(self.__rand_values))
                print('Saving random values succeeded...')

        except (IOError, IndexError):
            print('Saving random values failed....')

        if not is_received:
            for node in self.__peer_nodes:
                url = 'http://{}/broadcast-value'.format(node)
                try:
                    response = requests.post(url, json={'rand_value': rand_value})
                    print(url)
                    print(response.content)
                    if response.status_code == 400 or response.status_code == 500:
                        print('Error Value Broadcasting!')
                        return False
                except requests.exceptions.ConnectionError:
                    continue
        return True

    def add_block(self, block, proof_of_work):
        if not block:
            return None

        [nonce, hash_returned, hash_rate] = proof_of_work(self.__difficulty, self.get_last_block_header())

        if not hash_returned:
            return None

        t1 = time.time()

        incoming_block_pow_hash = block['block_header']['pow_hash']
        local_block_pow_hash = hash_returned
        incoming_block_prev_hash = block['block_header']['prev_block_hash']
        local_block_pow_hash2 = self.__blockchain[-1].__dict__['block_header']['pow_hash']

        incoming_block_index = block['block_header']['index']
        local_block_index = self.__blockchain[-1].__dict__['block_header']['index']

        print(incoming_block_pow_hash)
        print(local_block_pow_hash)
        print(incoming_block_prev_hash)
        print(local_block_pow_hash2)

        pow_incoming_block = block['block_header']['pow_hash']

        if local_block_pow_hash != incoming_block_pow_hash or incoming_block_prev_hash != local_block_pow_hash2 or \
                pow_incoming_block[0:self.__difficulty] != Utility.leading_zeros(self.__difficulty):
            return False

        # new_block = Block(block['block_header'], block['transactions'])
        new_block_header = BlockHeader(block['block_header']['version'],
                                       block['block_header']['block_id'],
                                       block['block_header']['prev_block_hash'],
                                       block['block_header']['pow_hash'],
                                       block['block_header']['merkle_tree_root'],
                                       block['block_header']['beneficiary'],
                                       block['block_header']['difficulty'],
                                       block['block_header']['index'],
                                       block['block_header']['nonce'],
                                       block['block_header']['hash_rate'],
                                       block['block_header']['timestamp']).__dict__

        new_transactions = [Transaction(t['sender'],
                                        t['recipient'],
                                        t['coins'],
                                        t['fees'],
                                        t['relay_fees'],
                                        t['signature']
                                        ).__dict__ for t in block['transactions']]

        new_block = Block(new_block_header, new_transactions)
        self.__blockchain.append(new_block)
        get_pending_transactions = self.__pending_transactions[:]
        for incoming_tx in block['transactions']:
            for open_tx in get_pending_transactions:
                if open_tx['sender'] == incoming_tx['sender'] and \
                        open_tx['recipient'] == incoming_tx['recipient'] and \
                        open_tx['coins'] == incoming_tx['coins'] and \
                        open_tx['fees'] == incoming_tx['fees'] and \
                        open_tx['relay_fees'] == incoming_tx['relay_fees'] and \
                        open_tx['signature'] == incoming_tx['signature']:
                    try:
                        self.__pending_transactions.remove(open_tx)
                    except ValueError:
                        print('Item was already removed!')
        self.save_blockchain()

        t2 = time.time()
        conf_time = t2 - t1
        print('Total Time: ' + str(conf_time))

        return True

    def resolve(self):
        curr_blockchain = self.__blockchain
        replace_blockchain = False
        for node in self.__peer_nodes:
            url = 'http://{}/blockchain'.format(node)
            try:
                response = requests.get(url)
                node_blockchain = response.json()
                # node_blockchain = [Block(block['block_header'], block['transactions']) for block in node_blockchain]
                # node_blockchain.transactions = [Transaction() for t in node_blockchain['transactions']]
                new_blockchain = []
                for block in node_blockchain:
                    new_block_header = BlockHeader(block['block_header']['version'],
                                                   block['block_header']['block_id'],
                                                   block['block_header']['prev_block_hash'],
                                                   block['block_header']['pow_hash'],
                                                   block['block_header']['merkle_tree_root'],
                                                   block['block_header']['beneficiary'],
                                                   block['block_header']['difficulty'],
                                                   block['block_header']['index'],
                                                   block['block_header']['nonce'],
                                                   block['block_header']['hash_rate'],
                                                   block['block_header']['timestamp']).__dict__

                    new_transactions = [Transaction(t['sender'],
                                                    t['recipient'],
                                                    t['coins'],
                                                    t['fees'],
                                                    t['relay_fees'],
                                                    t['signature']).__dict__ for t in block['transactions']]

                    new_block = Block(new_block_header, new_transactions)
                    new_blockchain.append(new_block)

                node_blockchain = new_blockchain
                node_blockchain_length = len(node_blockchain)
                local_blockchain_length = len(curr_blockchain)
                if node_blockchain_length > local_blockchain_length:
                    curr_blockchain = node_blockchain
                    replace_blockchain = True
            except requests.exceptions.ConnectionError:
                continue

        self.__resolve_conflicts = False
        self.__blockchain = curr_blockchain
        if replace_blockchain:
            self.__pending_transactions = []
        self.save_blockchain()
        return replace_blockchain

    def check_malicious_activity(self):
        local_ports = [5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010, 5011, 5012, 5013, 5014, 5015,
                       5016, 5017, 5018, 5019, 5020]
        results = []
        for i in local_ports:
            my_path = os.path.isfile('rand_value-{}.txt'.format(i))
            print(my_path)
            if my_path:
                print('port: ' + str(i))
                try:
                    with open('rand_value-{}.txt'.format(i), mode='r') as f:
                        content = json.loads(f.readline())
                        self.__rand_values = content
                    print('Loading random values succeeded...')
                except (ValueError, IOError, IndexError):
                    print('Error')

                init_conv = 0
                for j in self.__rand_values:
                    get1 = Utility.convert_string_to_binary(j)
                    get2 = Utility.convert_binary_to_base10(get1)
                    init_conv = init_conv ^ get2

                print(init_conv)
                results.append(init_conv)

                # conversion1 = Utility.convert_string_to_binary(self.__rand_values[0])
                # conversion2 = Utility.convert_string_to_binary(self.__rand_values[1])
                # conversion1 = Utility.convert_binary_to_base10(conversion1)
                # conversion2 = Utility.convert_binary_to_base10(conversion2)

                # print(conversion1 ^ conversion2)
                # target = conversion1 ^ conversion2
                # results.append(target)
                print('')
            else:
                print('File not found...')

        if len(results) > 0:
            num = 0
            target = results[0]
            for i in results:
                if i == target:
                    num += 1

            if num >= 2 * len(results) / 3:
                print('No malicious activity!')
                return True
            else:
                return False
        else:
            return False

    def add_peer_node(self, node):
        """Adds a new node to the peer node set.

        Arguments:
            :node: The node URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_blockchain()

    def remove_peer_node(self, node):
        """Removes a new node to the peer node set.

                Arguments:
                    :node: The node URL which should be removed.
                """
        self.__peer_nodes.discard(node)
        self.save_blockchain()

    def get_peer_nodes(self):
        return list(self.__peer_nodes)

    def send_hello(self):
        hello_message = {
            'message': 'hello peer discovery',
            'url': 'localhost:' + str(self.__node_id)
        }
        return hello_message

    def bootstrap_network(self, hello_message, is_received=False):
        if hello_message is None:
            return False

        if not is_received:
            for node in BOOTSTRAP_LIST:
                url = 'http://{}/peer-discovery-bootstrap'.format(node)
                try:
                    response = requests.post(url, json={'hello_message': self.send_hello()})
                    print(url)
                    print(response.content)
                    if response.status_code == 400 or response.status_code == 500:
                        print('Error Sending Hello Message!')
                        return False
                except requests.exceptions.ConnectionError:
                    continue
        return True

    def broadcast_to_peers(self, ack, is_received=False):
        if ack is None:
            return False

        url = 'localhost:' + str(self.__node_id)
        if not is_received:
            for node in self.__peer_nodes:
                url2 = 'http://{}/peer-acknowledgement'.format(node)
                try:
                    response = requests.post(url2, json={'ack': url})
                    print(url2)
                    print(response.content)
                    if response.status_code == 400 or response.status_code == 500:
                        print('Error Sending Hello Message!')
                        return False
                except requests.exceptions.ConnectionError:
                    continue
        return True
