#!/usr/bin/env python
"""
Roughly based on: http://code.activestate.com/recipes/576980-authenticated-encryption-with-pycrypto/
"""

import hashlib
import hmac
import base64

from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Util.number import long_to_bytes

__author__ = 'Dirk Moors'
__copyright__ = 'Copyright 2014, Dirk Moors'
__version__ = "1.0.0"
__status__ = "Production"

HASH_ALGO = hashlib.sha256

SIG_SIZE = HASH_ALGO().digest_size

class AuthenticationError(Exception):
    pass

def get_random_bytes(amount):
    return long_to_bytes(random.getrandbits(amount * 8))

def compare_mac(mac: bytes, mac_verif: bytes):
    if len(mac) != len(mac_verif):
        print("invalid MAC size")
        return False

    return mac == mac_verif

def encrypt(data: bytes, shared_key: bytes, hmac_key: bytes, iv_bytes: bytes = bytes(16 * [0])):
    """encrypt data with AES-CBC and sign it with HMAC-SHA256"""
    pad = AES.block_size - len(data) % AES.block_size
    data +=  bytes(pad * [pad])
    cypher = AES.new(shared_key, AES.MODE_CBC, iv_bytes)
    encrypted_data = cypher.encrypt(data)
    iv_data = iv_bytes + encrypted_data
    sig = hmac.new(hmac_key, iv_data, HASH_ALGO).digest()
    return (encrypted_data, sig)

def decrypt(encrypted_data: bytes, signature, shared_key, hmac_key,  iv_bytes: bytes = bytes(16 * [0])):
    """verify HMAC-SHA256 signature and decrypt data with AES-CBC"""
    iv_data = iv_bytes + encrypted_data
    if not compare_mac(hmac.new(hmac_key, iv_data, HASH_ALGO).digest(), signature):
        raise AuthenticationError("message authentication failed")
    cypher = AES.new(shared_key, AES.MODE_CBC, iv_bytes)
    data = cypher.decrypt(encrypted_data)
    return data[:-data[-1]]

if __name__ == "__main__":
    UID = bytes.fromhex('fb81c4cc20a3d5d1c700b89c4ebaecf786ea76c0518c7592119b6949f912d44e')
    data = bytes.fromhex('fb81c4cc20a3d5d1c700b89c4ebaecf786ea76c0518c7592119b6949f912d44eff61646d696e4061646d696e2e636f6d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000300040005000600070008000c00200400')
    
    (encrypted_data, signature) = encrypt(data, UID[::2], UID)
    print(f"{base64.b64encode(encrypted_data).decode()}.{base64.b64encode(signature).decode()}")
    decrypted_data = decrypt(encrypted_data, signature, UID[::2], UID)
    print(decrypted_data.hex())
    assert(decrypted_data == data)
