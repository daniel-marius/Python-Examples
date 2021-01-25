import base64
import binascii
import os
import time

from Crypto.Hash import SHA3_256, SHA256, SHA1
from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS


class Wallet:

    def __init__(self, node_id):
        self.__node_id = node_id
        self.__salt = None
        self.__user_address = None

    @property
    def node_id(self):
        return self.__node_id

    @node_id.setter
    def node_id(self, node_id):
        self.__node_id = node_id

    @property
    def salt(self):
        return self.__salt

    @salt.setter
    def salt(self, salt):
        self.__salt = salt

    @property
    def user_address(self):
        return self.__user_address

    @user_address.setter
    def user_address(self, user_address):
        self.__user_address = user_address

    def generate_master_private_key(self):
        t1 = time.time()
        password = 'password'
        salt = 'salt'
        dklen = 16
        count = self.__node_id - 1000
        msk = PBKDF2(password=password,
                     salt=salt.encode(),
                     dkLen=dklen,
                     count=count,
                     hmac_hash_module=SHA256)
        t2 = time.time()
        print('Create Master Private Key: ' + str(t2 - t1))
        return msk

    def generate_master_public_key(self, count=1000, dklen=16):
        t1 = time.time()
        mpk = PBKDF2(password=str(self.generate_master_private_key()),
                     salt=self.__salt,
                     dkLen=dklen,
                     count=count,
                     hmac_hash_module=SHA256)
        t2 = time.time()
        print('Create Master Public Key: ' + str(t2 - t1))
        return mpk

    def generate_keys(self):
        t1 = time.time()
        key = ECC.generate(curve='P-256', randfunc=self.generate_master_public_key)
        t2 = time.time()
        print('Create ECC Keys: ' + str(t2 - t1))
        return key

    def create_save_keys(self):
        key = self.generate_keys()
        private_key = key.export_key(format='PEM')
        f = open('private_key-{}.pem'.format(self.__node_id), 'wt')
        f.write(private_key)
        f.close()

        public_key = key.public_key().export_key(format='PEM')
        f = open('public_key-{}.pem'.format(self.__node_id), 'wt')
        f.write(public_key)
        f.close()

    def generate_user_address(self):
        t1 = time.time()
        key = ECC.import_key(open('public_key-{}.pem'.format(self.__node_id)).read())
        step1 = SHA1.new(str(key).encode())
        step2 = SHA256.new(str(step1).encode())
        step3 = SHA3_256.new(str(step2).encode())
        b64 = base64.b64encode((step3.digest())).decode()
        final_address = 'DM' + str(b64[:-1])
        t2 = time.time()
        print('Create User Address: ' + str(t2 - t1))
        return final_address

    def create_user_address(self):
        self.__user_address = self.generate_user_address()

    def save_user_address(self):
        if self.user_address is not None:
            try:
                with open('user_address-{}.txt'.format(self.__node_id), mode='w') as file:
                    file.write(self.__user_address)
                print('Saving user address succeeded...')
                return True
            except(IOError, IndexError, ValueError):
                print('Saving user address failed...')
                return False

    def load_user_address(self):
        try:
            with open('user_address-{}.txt'.format(self.__node_id), mode='r') as file:
                self.user_address = file.read()
            print('Loading user address...')
            return True
        except(IOError, IndexError, ValueError):
            print('Loading user address...')
            return False

    def delete_user_address(self):
        try:
            os.remove('user_address-{}.txt'.format(self.__node_id))
            print('File removed...')
            return True
        except(IOError, IndexError, ValueError):
            print('File not found...')
            return False

    def sign_transaction(self, sender, recipient, coins, fees, relay_fees):
        message = str(sender) + \
                  str(recipient) + \
                  str(coins) + \
                  str(fees) + \
                  str(relay_fees)
        h = SHA3_256.new(message.encode())
        key = None
        try:
            key = ECC.import_key(open('private_key-{}.pem'.format(self.__node_id)).read())
        except(IOError, IndexError, ValueError):
            pass
        signer = DSS.new(key, 'fips-186-3')
        signature = signer.sign(h)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction(transaction):
        message = str(transaction.sender) + \
                  str(transaction.recipient) + \
                  str(transaction.coins) + \
                  str(transaction.fees) + \
                  str(transaction.relay_fees)
        h = SHA3_256.new(message.encode())
        local_port = [5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010, 5011, 5012, 5013, 5014, 5015,
                      5016, 5017, 5018, 5019, 5020]
        found = False
        for i in local_port:
            my_path = os.path.isfile('public_key-{}.pem'.format(i))
            if my_path:
                key = ECC.import_key(open('public_key-{}.pem'.format(i)).read())
                verifier = DSS.new(key, 'fips-186-3')
                try:
                    verifier.verify(h, binascii.unhexlify(transaction.signature))
                    found = True
                except (IOError, ValueError):
                    found = True
                break
            else:
                print('File not found')
        print(found)
        return found

    @staticmethod
    def verify_transaction2(transaction):
        message = str(transaction['sender']) + \
                  str(transaction['recipient']) + \
                  str(transaction['coins']) + \
                  str(transaction['fees']) + \
                  str(transaction['relay_fees'])
        h = SHA3_256.new(message.encode())
        local_port = [5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010, 5011, 5012, 5013, 5014, 5015,
                      5016, 5017, 5018, 5019, 5020]
        found = False
        for i in local_port:
            my_path = os.path.isfile('public_key-{}.pem'.format(i))
            if my_path:
                key = ECC.import_key(open('public_key-{}.pem'.format(i)).read())
                verifier = DSS.new(key, 'fips-186-3')
                try:
                    verifier.verify(h, binascii.unhexlify(transaction['signature']))
                    found = True
                except (IOError, ValueError):
                    found = True
                break
            else:
                print('File not found...')
        return found
