import base64
import binascii
import re

from Crypto.Random import get_random_bytes


class Utility:

    def __init__(self):
        pass

    @staticmethod
    def symmetric_key_generation():
        return get_random_bytes(16)

    @staticmethod
    def convert_everything_to_bytes(item):
        everything_bytes = bytes(str(item), 'utf-8')
        return everything_bytes

    @staticmethod
    def convert_int_to_bytes(integer):
        int_to_bytes = int.from_bytes(integer, byteorder='big')
        return int_to_bytes

    @staticmethod
    def convert_string_to_binary(string):
        string_bytes = bytes(string, 'ascii')
        string_binary = ''.join("{0:b}".format(item) for item in string_bytes)
        return string_binary

    @staticmethod
    def convert_string_to_binary_2(string):
        string_binary = ''.join(format(ord(item), 'b') for item in string)
        return string_binary

    @staticmethod
    def convert_binary_to_base10(binary_input):
        binary_array = int(binary_input, 2)
        return binary_array

    @staticmethod
    def leading_zeros(difficulty):
        zeros = ''
        for i in range(0, difficulty):
            zeros += '0'
        return zeros

    @staticmethod
    def check_address_format(address):
        if len(address) < 45:
            return False

        if len(address) > 45:
            return False

        if len(address) == 45:
            new_address = address[1:]
            try:
                if type(new_address) == str:
                    # If there's any unicode here, an exception will be thrown and the function will return false.
                    sb_bytes = bytes(new_address, 'ascii')
                elif type(new_address) == bytes:
                    sb_bytes = new_address
                else:
                    raise ValueError("Argument must be string or bytes")
                # If the re-encoded string is equal to the encoded string, then it is base64 encoded.
                return base64.b64encode(base64.b64decode(sb_bytes, validate=True)) == sb_bytes
            except binascii.Error:
                return False

    @staticmethod
    def check_address_format2(address):
        """ Checking the string header to see if it matches that of a base64 encoded string """
        pattern = re.compile("^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$")
        if len(address) < 45:
            return False

        if len(address) > 45:
            return False

        if len(address) == 45:
            new_address = address[1:]
            return pattern.match(new_address)
