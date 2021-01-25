from Crypto.Random import get_random_bytes
from ecc_wallet import Wallet
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from proof_of_work import ProofOfWork
from verification import Verification

from blockchain import Blockchain

SCRYPT_ARRAY_SIZE = 512

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'web_node.html')


@app.route('/network', methods=['GET'])
def get_network():
    return send_from_directory('ui', 'network.html')


@app.route('/pending_transactions', methods=['GET'])
def get_pending():
    return send_from_directory('ui', 'pending_transactions.html')


@app.route('/wallet', methods=['POST'])
def create_keys_address():
    wallet_ecc.salt = get_random_bytes(10)

    if wallet_ecc.generate_keys() is not None:
        wallet_ecc.create_save_keys()
        wallet_ecc.create_user_address()
        wallet_ecc.save_user_address()

        global blockchain_obj
        blockchain_obj = Blockchain(wallet_ecc.user_address, port)

        response = {
            'user_address': wallet_ecc.user_address,
            'funds': blockchain_obj.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving ECC keys and user address failed!'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_key_address():
    if wallet_ecc.load_user_address():
        global blockchain_obj
        blockchain_obj = Blockchain(wallet_ecc.user_address, port)

        response = {
            'user_address': wallet_ecc.user_address,
            'funds': blockchain_obj.get_balance()
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading user address failed!'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain_obj.get_balance(wallet_ecc.user_address)
    if balance is not None:
        response = {
            'message': 'Loading balance successfully!',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading balance failed!',
            'wallet_set_up': wallet_ecc.user_address is not None
        }
        return jsonify(response), 500


@app.route('/broadcast-value', methods=['POST'])
def broadcast_value():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached!'
        }
        return jsonify(response), 400
    required = ['rand_value']
    if not all(key in values for key in required):
        response = {
            'message': 'Some data is missing!'
        }
        return jsonify(response), 400
    rand_value = values['rand_value']
    success = blockchain_obj.broadcast_value(rand_value, is_received=True)
    if success:
        response = {
            'message': 'Successfully broadcast value!',
            'rand_value': values['rand_value']
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a value failed (broadcast value)!'
        }
        return jsonify(response), 500


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found!'
        }
        return jsonify(response), 400
    print(values)
    required = ['sender', 'recipient', 'coins', 'fees', 'relay_fees', 'signature']
    print(required)
    if not all(key in values for key in required):
        response = {
            'message': 'Some data is missing (broadcast transaction)!'
        }
        return jsonify(response), 400
    success = blockchain_obj.add_transaction(values['sender'],
                                             values['recipient'],
                                             values['coins'],
                                             values['fees'],
                                             values['relay_fees'],
                                             values['signature'],
                                             is_received=True)
    if success:
        response = {
            'message': 'Successfully broadcast transaction!',
            'transaction': {
                'sender': values['sender'],
                'recipient': values['recipient'],
                'coins': values['coins'],
                'fees': values['fees'],
                'relay_fees': values['relay_fees'],
                'signature': values['signature']
            }
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed (broadcast transaction)!'
        }
        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found!'
        }
        return jsonify(response), 400
    if 'block' not in values:
        response = {
            'message': 'Some data is missing!'
        }
        return jsonify(response), 400
    block = values['block']
    if block['block_header']['index'] == blockchain_obj.blockchain[-1].__dict__['block_header']['index'] + 1:
        if blockchain_obj.add_block(block, proof_of_work_obj.proof_of_work):
            response = {
                'message': 'Block added!'
            }
            return jsonify(response), 201
        else:
            response = {
                'message': 'Block seems invalid!'
            }
            return jsonify(response), 409
    elif block['block_header']['index'] > blockchain_obj.blockchain[-1].__dict__['block_header']['index']:
        response = {
            'message': 'Blockchain seems to be shorter than local blockchain!'
        }
        blockchain_obj.resolve_conflicts = True
        return jsonify(response), 200
    else:
        response = {
            'message': 'Blockchain seems to be shorter, block not added!'
        }
        return jsonify(response), 409


@app.route('/value', methods=['POST'])
def add_value():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached!'
        }
        return jsonify(response), 400
    if 'rand_value' not in values:
        response = {
            'message': 'No data attached!'
        }
        return jsonify(response), 400
    rand_value = values['rand_value']
    success = blockchain_obj.broadcast_value(rand_value)
    if success:
        response = {
            'message': 'Value added successfully!',
            'all_values': blockchain_obj.rand_values
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Value not added!'
        }
        return jsonify(response), 500


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet_ecc.user_address is None:
        response = {
            'message': 'No wallet!'
        }
        return jsonify(response), 400
    values = request.get_json()
    print(values)
    if not values:
        response = {
            'message': 'No data found!'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'coins', 'fees', 'relay_fees']
    print(required_fields)
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing (transaction)!'
        }
        return jsonify(response), 400

    recipient = values['recipient']
    coins = values['coins']
    fees = values['fees']
    relay_fees = values['relay_fees']
    signature = wallet_ecc.sign_transaction(wallet_ecc.user_address,
                                            recipient,
                                            coins,
                                            fees,
                                            relay_fees)
    success = blockchain_obj.add_transaction(wallet_ecc.user_address,
                                             recipient,
                                             coins,
                                             fees,
                                             relay_fees,
                                             signature)
    if success:
        response = {
            'message': 'Successfully added transaction!',
            'transaction': {
                'sender': wallet_ecc.user_address,
                'recipient': recipient,
                'coins': coins,
                'fees': fees,
                'relay_fees': relay_fees,
                'signature': signature
            },
            'funds': blockchain_obj.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed! Possible double-spending or mempool flooding!'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine_block():
    if blockchain_obj.resolve_conflicts:
        response = {
            'message': 'Resolve conflicts first, block not added!'
        }
        return jsonify(response), 409

    block = blockchain_obj.mine_block(proof_of_work_obj.proof_of_work)

    if block is not None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx for tx in dict_block['transactions']]
        response = {
            'message': 'Block mined successfully!',
            'block': dict_block,
            'funds': blockchain_obj.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed!',
            'wallet_set_up': wallet_ecc.user_address is not None
        }
        return jsonify(response), 500


@app.route('/selfish-mining', methods=['POST'])
def selfish_mining():
    block = blockchain_obj.selfish_mining(proof_of_work_obj.proof_of_work)

    if block is not None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx for tx in dict_block['transactions']]
        response = {
            'message': 'Block mined successfully!',
            'block': dict_block,
            'funds': blockchain_obj.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed!',
            'wallet_set_up': wallet_ecc.user_address is not None
        }
        return jsonify(response), 500


@app.route('/filter-mempool', methods=['POST'])
def filter_mempool():
    new_mempool = blockchain_obj.filter_transaction_pool()
    if new_mempool:
        response = {
            'message': 'Memory Pool was filtered!'
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Memory Pool was not filtered (possible empty memory pool)!'
        }
        return jsonify(response), 400


@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced_blockchain = blockchain_obj.resolve()
    if replaced_blockchain:
        response = {
            'message': 'Blockchain was replaced!'
        }
    else:
        response = {
            'message': 'Local blockchain kept!'
        }
    return jsonify(response), 200


@app.route('/check-activity', methods=['POST'])
def check_activity():
    activity = blockchain_obj.check_malicious_activity()
    if activity:
        response = {
            'message': 'No malicious activity reported!'
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Malicious activity detected!'
        }
        return jsonify(response), 400


@app.route('/change-difficulty', methods=['POST'])
def change_difficulty():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached!'
        }
        return jsonify(response), 400
    if 'difficulty' not in values:
        response = {
            'message': 'No data attached!'
        }
        return jsonify(response), 400

    difficulty = values['difficulty']
    success = blockchain_obj.set_new_difficulty(difficulty)
    if success:
        response = {
            'message': 'New difficulty saved!',
            'difficulty': difficulty
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'New difficulty not saved!'
        }
        return jsonify(response), 400


@app.route('/peer-discovery', methods=['POST'])
def finding_server():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No message attached!'
        }
        return jsonify(response), 400
    print(values)
    if 'hello_message' not in values:
        response = {
            'message': 'No message attached!'
        }
        return jsonify(response), 400
    hello_message = values['hello_message']
    success = blockchain_obj.bootstrap_network(hello_message)
    if success:
        response = {
            'message': 'Hello message sent!',
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Hello message not sent!'
        }
        return jsonify(response), 500


@app.route('/peer-discovery-bootstrap', methods=['POST'])
def finding_server_bootstrap():
    values = request.get_json()
    print(values)
    if not values:
        response = {
            'message': 'No message attached!'
        }
        return jsonify(response), 400
    if 'hello_message' not in values:
        response = {
            'message': 'No message attached!'
        }
        return jsonify(response), 400
    hello_message = values['hello_message']
    print(hello_message)
    success = blockchain_obj.bootstrap_network(hello_message, is_received=True)
    if success:
        response = {
            'message': 'Hello message sent!',
        }
        blockchain_obj.add_peer_node(hello_message['url'])
        return jsonify(response), 201
    else:
        response = {
            'message': 'Hello message not sent!'
        }
        return jsonify(response), 500


@app.route('/peer', methods=['POST'])
def peer():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No message attached!'
        }
        return jsonify(response), 400
    print(values)
    if 'ack' not in values:
        response = {
            'message': 'No message attached!'
        }
        return jsonify(response), 400
    ack = values['ack']
    success = blockchain_obj.broadcast_to_peers(ack)
    if success:
        response = {
            'message': 'Ack message sent!',
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Ack message not sent!'
        }
        return jsonify(response), 500


@app.route('/peer-acknowledgement', methods=['POST'])
def peer_ackowledgement():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No message attached!'
        }
        return jsonify(response), 400
    if 'ack' not in values:
        response = {
            'message': 'No message attached!'
        }
        return jsonify(response), 400
    ack = values['ack']
    success = blockchain_obj.broadcast_to_peers(ack, is_received=True)
    if success:
        response = {
            'message': 'Ack!',
        }
        blockchain_obj.add_peer_node(ack)
        return jsonify(response), 201
    else:
        response = {
            'message': 'Not Ack!'
        }
        return jsonify(response), 500


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    transactions = blockchain_obj.pending_transactions
    dict_transactions = [tx for tx in transactions]
    response = {
        'message': 'Transactions!',
        'transactions': dict_transactions
    }
    return jsonify(response), 200


@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    blockchain_snapshot = blockchain_obj.blockchain
    # converting a chain of blocks to a chain of dictionaries
    dict_blockchain = [block.__dict__.copy() for block in blockchain_snapshot]
    for dict_block in dict_blockchain:
        dict_block['transactions'] = [tx for tx in dict_block['transactions']]
    return jsonify(dict_blockchain), 200


@app.route('/valid', methods=['GET'])
def get_blockchain_validation():
    get_blockchain_valid = Verification.verify_blockchain(blockchain_obj.blockchain,
                                                          blockchain_obj.difficulty,
                                                          proof_of_work_obj.proof_of_work)
    if get_blockchain_valid is True:
        response = {
            'message': 'Chain is valid!'
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Chain is not valid!'
        }
        return jsonify(response), 400


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached!'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'No data attached!'
        }
        return jsonify(response), 400
    node = values['node']
    blockchain_obj.add_peer_node(node)
    response = {
        'message': 'Node added successfully!',
        'all_nodes': blockchain_obj.get_peer_nodes()
    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url is None:
        response = {
            'message': 'No node found!'
        }
        return jsonify(response), 400
    blockchain_obj.remove_peer_node(node_url)
    response = {
        'message': 'Node removed',
        'all_node': blockchain_obj.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = blockchain_obj.get_peer_nodes()
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    proof_of_work_obj = ProofOfWork(SCRYPT_ARRAY_SIZE)
    wallet_ecc = Wallet(port)
    blockchain_obj = Blockchain(wallet_ecc.user_address, port)
    app.run(host='localhost', port=port)
