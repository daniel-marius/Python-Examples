import binascii
import json
import os
from base64 import b64encode, b64decode

import Crypto.Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from utility import Utility

RSA_KEY_SIZE = 2048


class Wallet:

    def __init__(self, node_id):
        self.__private_key = None
        self.__public_key = None
        self.__node_id = node_id

    @property
    def private_key(self):
        return self.__private_key

    @private_key.setter
    def private_key(self, private_key):
        self.__private_key = private_key

    @property
    def public_key(self):
        return self.__public_key

    @public_key.setter
    def public_key(self, public_key):
        self.__public_key = public_key

    @staticmethod
    def symmetric_encryption(symmetric_key, data):
        header = b"header"
        cipher = AES.new(symmetric_key, AES.MODE_EAX)
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        crypto_array = [cipher.nonce, header, ciphertext, tag]
        json_k = ['nonce', 'header', 'ciphertext', 'tag']
        json_v = [b64encode(x).decode('utf-8') for x in crypto_array]
        result = json.dumps(dict(zip(json_k, json_v)))
        return result

    @staticmethod
    def symmetric_decryption(symmetric_key, result):
        try:
            b64 = json.loads(result)
            json_k = ['nonce', 'header', 'ciphertext', 'tag']
            jv = {k: b64decode(b64[k]) for k in json_k}

            cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=jv['nonce'])
            cipher.update(jv['header'])
            plaintext = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])
            return plaintext
        except (ValueError, KeyError):
            print("Incorrent decryption")
        finally:
            print('Cleaning...')

    @staticmethod
    def generate_keys():
        private_key = RSA.generate(RSA_KEY_SIZE, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key.exportKey(format='DER')),
                binascii.hexlify(public_key.exportKey(format='DER')))

    def create_keys(self):
        (private_key, public_key) = self.generate_keys()
        self.__private_key = private_key.decode()
        self.__public_key = public_key.decode()

    def save_keys(self):
        if self.__public_key is not None and self.__private_key is not None:
            try:
                with open('wallet-{}.txt'.format(self.__node_id), mode='w') as f:
                    plaintext_public_key = str.encode(self.__public_key)
                    plaintext_private_key = str.encode(self.__private_key)

                    symmetric_key_1 = Utility.symmetric_key_generation()
                    symmetric_key_2 = Utility.symmetric_key_generation()

                    json_result_1 = self.symmetric_encryption(symmetric_key_1, plaintext_public_key)
                    json_result_2 = self.symmetric_encryption(symmetric_key_2, plaintext_private_key)

                    symm_key_1 = b64encode(symmetric_key_1).decode('utf-8')
                    symm_key_2 = b64encode(symmetric_key_2).decode('utf-8')

                    f.write(json_result_1)
                    f.write('\n')

                    f.write(symm_key_1)
                    f.write('\n')

                    f.write(json_result_2)
                    f.write('\n')

                    f.write(symm_key_2)
                return True
            except(IOError, IndexError):
                print('Saving wallet failed...')
                return False
            finally:
                print('Cleaning...')

    def load_keys(self):
        try:
            with open('wallet-{}.txt'.format(self.__node_id), mode='r') as f:
                encrypted_lines = f.readlines()

                encrypted_public_key = encrypted_lines[0][:-1]
                symmetric_key_1 = encrypted_lines[1][:-1]

                encrypted_private_key = encrypted_lines[2][:-1]
                symmetric_key_2 = encrypted_lines[3]

                decrypted_public_key = self.symmetric_decryption(b64decode(symmetric_key_1), encrypted_public_key)
                decrypted_private_key = self.symmetric_decryption(b64decode(symmetric_key_2), encrypted_private_key)

                self.__public_key = str(decrypted_public_key, "utf-8")
                self.__private_key = str(decrypted_private_key, "utf-8")
            return True
        except(IOError, IndexError):
            print('Loading wallet failed...')
            return False
        finally:
            print('Cleaning...')

    @staticmethod
    def delete_keys():
        try:
            os.remove('wallet.txt')
            print('File removed...')
        except(IOError, SystemError):
            print('File not found...')
        finally:
            print('Cleaning...')

    def sign_transaction(self, transaction):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.__private_key)))
        signature = signer.sign(transaction.transaction_id)
        return binascii.hexlify(signature).decode()

    @staticmethod
    def verify_transaction(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        try:
            print("The signature is valid...")
            return verifier.verify(transaction.transaction_id, binascii.unhexlify(transaction.signature))
        except (ValueError, TypeError):
            print("The signature is not valid...")
        finally:
            print('Cleanup...')
        return False

    @staticmethod
    def verify_transaction_2(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction['sender']))
        verifier = PKCS1_v1_5.new(public_key)
        try:
            print("The signature is valid...")
            return verifier.verify(transaction['transaction_id'], binascii.unhexlify(transaction['signature']))
        except (ValueError, TypeError):
            print("The signature is not valid...")
        finally:
            print('Cleanup...')
        return False
