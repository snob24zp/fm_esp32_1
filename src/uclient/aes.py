"""
AES abstraction layer
"""
import sys

if sys.version.count('MicroPython') > 0:
    from ucryptolib import aes
else:
    from Crypto.Cipher import AES

def cipher(key, iv):
    if sys.version.count('MicroPython') > 0:
        return aes(key, 2, iv)

    return AES.new(key, AES.MODE_CBC, iv)


def decrypt(data: bytes, key: bytes, iv=bytes(16)) -> bytes:
    data = cipher(key, iv).decrypt(data)
    return data[:-data[-1]]

def encrypt(data: bytes, key: bytes, iv=bytes(16)) -> bytes:
    pad = AES.block_size - len(data) % AES.block_size
    data +=  bytes(pad * [pad])
    return cipher(key, iv).encrypt(data)