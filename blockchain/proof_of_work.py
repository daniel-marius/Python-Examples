import json
import time

from Crypto.Hash import SHA256, SHA3_256
from merkle_tree import MerkleTree
from utility import Utility


class ProofOfWork:

    def __init__(self, input_size=0):
        self.__input_size = input_size
        self.__array = [''] * self.__input_size
        # self.__save_time_diff = []
        # self.load_diff_time()

    @property
    def input_size(self):
        return self.__input_size

    @input_size.setter
    def input_size(self, input_size):
        self.__input_size = input_size

    def __len__(self):
        return len(self.__array)

    def __getitem__(self, index):
        return self.__array[index]

    def save_diff_time(self):
        try:
            with open('pow-time.txt', mode='w') as f:
                f.write(json.dumps(self.__save_time_diff))
                print('Saving Block Time...')
        except (IOError, IndexError):
            print('Error Saving Block Time!')

    def load_diff_time(self):
        try:
            with open('pow-time.txt', mode='r') as f:
                file_content = f.readline()
                self.__save_time_diff = json.loads(file_content)
                print('Loading Block Time...')
        except (IOError, IndexError):
            print('Error Loading Block Time!')

    def scrypt_method_sha2(self, seed):
        self.__array[0] = seed

        for i in range(1, self.__input_size):
            self.__array[i] = SHA256.new(self.__array[i - 1].encode()).hexdigest()

        x = self.__array[-1]
        for i in range(1, self.__input_size):
            convert_x = int(x, 16)
            j = convert_x % self.__input_size

            convert_j = int(self.__array[j], 16)
            result = convert_x ^ convert_j

            x = SHA256.new(str(result).encode()).hexdigest()

        return x

    def scrypt_method_sha3(self, seed):
        self.__array[0] = seed

        for i in range(1, self.__input_size):
            self.__array[i] = SHA3_256.new(self.__array[i - 1].encode()).hexdigest()

        x = self.__array[-1]
        for i in range(1, self.__input_size):
            convert_x = int(x, 16)
            j = convert_x % self.__input_size

            convert_j = int(self.__array[j], 16)
            result = convert_x ^ convert_j

            x = SHA3_256.new(str(result).encode()).hexdigest()

        return x

    def proof_of_work(self, difficulty, get_last_block_header):

        nonce = 0
        start_time = time.time()

        while True:

            last_block_header = get_last_block_header.copy()
            block_header_string = (str(last_block_header['version']) +
                                   str(last_block_header['block_id']) +
                                   str(last_block_header['prev_block_hash']) +
                                   str(last_block_header['merkle_tree_root']) +
                                   str(last_block_header['beneficiary']) +
                                   str(last_block_header['difficulty']) +
                                   str(last_block_header['index']) +
                                   str(nonce))
            seed = block_header_string
            seed = SHA3_256.new(json.dumps(seed, sort_keys=True).encode()).hexdigest()
            get_proof = self.scrypt_method_sha3(seed)

            print('Hash: {}'.format(get_proof))
            print('Counter: {}'.format(str(nonce)))

            if get_proof[0:difficulty] == Utility.leading_zeros(difficulty):
                result = get_proof
                break

            nonce += 1

        end_time = time.time()

        print("Success with nonce: {}".format(str(nonce)))
        print("Hash: {}".format(result))
        print("Elapsed Time: {}".format(str(end_time - start_time) + " seconds"))

        pair = (difficulty, end_time - start_time)

        # self.__save_time_diff.append(pair)
        # self.save_diff_time()

        hash_rate = ''
        if end_time - start_time > 0:
            hash_power = float(nonce / (end_time - start_time))
            print("Hashing Power: {} hashes per second".format(str(hash_power)))
            hash_rate = str(hash_power) + " hashes/second"
        return [nonce, result, hash_rate]

    def get_scrypt_pow(self, seed, difficulty):

        nonce = 0
        start_time = time.time()

        zeros = ''
        for i in range(0, difficulty):
            zeros += '0'

        while True:
            get_seed = str(seed) + str(nonce)
            get_seed = SHA3_256.new(json.dumps(get_seed, sort_keys=True).encode()).hexdigest()
            get_proof = self.scrypt_method_sha3(get_seed)

            # print('Hash: {}'.format(get_proof))
            # print('Counter: {}'.format(str(nonce)))

            if get_proof[0:difficulty] == Utility.leading_zeros(difficulty):
                result = get_proof
                break

            nonce += 1

        end_time = time.time()

        print("Success with nonce: {}".format(str(nonce)))
        print("Hash: {}".format(result))
        print("Elapsed Time: {}".format(str(end_time - start_time) + " seconds"))

        return result

    @staticmethod
    def build_random_data(random_data_size):
        random_data = []
        for i in range(0, random_data_size):
            get_random = i
            get_hash = SHA3_256.new(str(get_random).encode())
            random_data.append(get_hash.hexdigest())

        return random_data

    @staticmethod
    def build_list_pair(random_data):
        list_pair = []
        tree_leaves = random_data
        while len(tree_leaves) > 0:
            x = tree_leaves[0]
            y = tree_leaves[1]
            tree_leaves.remove(x)
            tree_leaves.remove(y)
            pair = (x, y)
            list_pair.append(pair)
        return list_pair

    @staticmethod
    def build_merkle_tree(random_data):
        v = random_data
        mt = MerkleTree()
        return mt.merkle_tree_construct(v)

    @staticmethod
    def scratch(list_pair, digest, puz, q):

        sigma_h_con = ''
        sigma_h = []

        get_list_pair = list_pair

        r = 'r'
        seed = str(r) + str(digest) + str(puz)
        h = SHA3_256.new(seed.encode()).hexdigest()

        for i in range(0, q):
            x = get_list_pair[i][0]
            y = get_list_pair[i][1]
            sigma_h.append((x, y))
            sigma_h_con = sigma_h_con + str(x) + str(y)

        new_seed = str(puz) + str(r) + str(sigma_h_con)
        return [new_seed, r, sigma_h_con, h]

    @staticmethod
    def scratch2(new_puz, r, sigma_h_con):
        solution_pair = ''
        if new_puz is not None:
            solution_pair = (r, sigma_h_con)
        return solution_pair

    @staticmethod
    def sign_payload(puz, digest, message, list_pair, q):

        seed_local = str(puz) + str(digest) + str(message)
        h_prime = SHA3_256.new(seed_local.encode()).hexdigest()

        sigma_h_prime = []
        sigma_h_prime_con = ''
        for i in range(q, len(list_pair)):
            x = list_pair[i][0]
            y = list_pair[i][1]
            sigma_h_prime.append((x, y))
            sigma_h_prime_con = sigma_h_prime_con + str(x) + str(y)

        return [sigma_h_prime_con, h_prime]

    @staticmethod
    def verify_ticket(ticket, puz, message, h, h_prime):
        local_seed_h = str(ticket[1]) + str(ticket[0]) + str(puz)
        local_seed_h_prime = str(puz) + str(ticket[0]) + str(message)
        new_h = SHA3_256.new(local_seed_h.encode()).hexdigest()
        new_h_prime = SHA3_256.new(local_seed_h_prime.encode()).hexdigest()
        if h == new_h and h_prime == new_h_prime:
            return True
        else:
            return False


# p = ProofOfWork(10)

# rand_data = ProofOfWork.build_random_data(14)
# dig = ProofOfWork.build_merkle_tree(rand_data)
# list_pairs = ProofOfWork.build_list_pair(rand_data)
# diff = 2
# seed = 'seed'
# q = 2
# puz = p.get_scrypt_pow(seed, diff)
# [new_seed, r, sigma_h_con, h] = ProofOfWork.scratch(list_pairs, dig, puz, q)
# new_puz = p.get_scrypt_pow(new_seed, diff)
# res_scratch = p.scratch2(new_puz, r, sigma_h_con)

# [sigma_h_prime_con, h_prime] = ProofOfWork.sign_payload(puz, dig, 'message', list_pairs, q)
# ticket = [dig, r, sigma_h_con, sigma_h_prime_con]

# if ProofOfWork.verify_ticket(ticket, puz, 'message', h, h_prime):
# print('Valid ticket!')
# else:
# print('Invalid ticket!')

# Create figure for plotting

# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1)
# xs = np.array([0.24234914779663086, 28.04440665245056, 20.447636127471924, 4287.642205953598])
# ys = np.array([1, 2, 3, 4])

# Draw plot
# ax.plot(xs, ys)

# Format plot
# plt.xticks(rotation=60, ha='right')
# plt.subplots_adjust(bottom=0.30)
# plt.title('Block Time with SHA3-256')
# plt.ylabel('Difficulty')
# plt.xlabel('Seconds')

# Draw the graph
# plt.show()


import matplotlib.pyplot as plt

plt.style.use('classic')
# import numpy as np

# import seaborn as sns

# sns.set()

# df = pd.DataFrame({"Difficulty": [1, 2, 3, 4, 5],
#                   "Time (seconds)": [0.00790262222290039, 0.40659594535827637, 2.155961036682129, 122.07845544815063,
#                                      244.15928769111633]})

# df2 = pd.DataFrame({"Difficulty": [1, 2, 3, 4, 5],
#                    "Time (seconds)": [0.027921438217163086, 0.10732364654541016,  6.024337530136108, 141.9519305229187,
#                                       1017.7891993522644]})

# df3 = pd.DataFrame({"Difficulty": [1, 2, 3, 4, 5],
#                     "Time (seconds)": [0.5213141441345215, 9.253600358963013, 187.9258840084076, 180.53885674476624,
#                                        4600.46457567546]})

# df4 = pd.DataFrame({"Difficulty": [1, 2, 3, 4, 5],
#                    "Time (seconds)": [0.583076000213623, 6.783142566680908, 131.5194330215454, 1268.5340614318848,
#                                       5000.45674624353]})

# fig, axes = plt.subplots(nrows=2, ncols=2)
# fig.tight_layout()

# df.head()
# df2.head()
# axes[0, 0].set_title('Block Time SHA3-256 N=16')
# axes[0, 1].set_title('Block Time SHA256 N=16')
# axes[1, 0].set_title('Block Time SHA3-256 N=512')
# axes[1, 1].set_title('Block Time SHA256 N=512')
# df.plot(ax=axes[0, 0], linewidth=3, fontsize=12)
# df2.plot(ax=axes[0, 1], linewidth=3, fontsize=12)
# df3.plot(ax=axes[1, 0], linewidth=3, fontsize=12)
# df4.plot(ax=axes[1, 1], linewidth=3, fontsize=12)
# sns.lineplot(x="Seconds", y="Difficulty", data=df)
# sns.lineplot(x="Seconds", y="Difficulty", data=df2)
# plt.xticks(rotation=15)
# plt.show()
