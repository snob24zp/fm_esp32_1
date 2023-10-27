import hashlib

trans_5C = bytes((x ^ 0x5C) for x in range(256))
trans_36 = bytes((x ^ 0x36) for x in range(256))

def translate(d, t):
    return bytes(t[x] for x in d)

digest_size = None

class HMAC:
    blocksize = 64 

    def __init__(self, key, msg = None, digestmod = hashlib.sha256, digest_size = 16):
        if not isinstance(key, (bytes, bytearray)):
            raise TypeError("key: expected bytes or bytearray, but got %r" % type(key).__name__)

        self.digest_cons = digestmod

        self.outer = self.digest_cons()
        self.inner = self.digest_cons()
        self.digest_size = digest_size

        if hasattr(self.inner, 'block_size'):
            blocksize = self.inner.block_size
            if blocksize < 16:
                blocksize = self.blocksize
        else:
            blocksize = self.blocksize

        self.block_size = blocksize

        if len(key) > blocksize:
            key = self.digest_cons(key).digest()

        key = key + bytes(blocksize - len(key))
        self.outer.update(translate(key, trans_5C))
        self.inner.update(translate(key, trans_36))
        self.finalized = False
        if msg is not None:
            self.update(msg)

    @property
    def name(self):
        return "hmac-" + self.inner.name

    def update(self, msg):
        if self.finalized:
            raise ValueError("Cannot call .update() after .digest()")
        self.inner.update(msg)


    def _current(self):
        self.finalized = True
        h = self.outer
        h.update(self.inner.digest())
        return h

    def digest(self):
        h = self._current()
        return h.digest()

    def hexdigest(self):
        h = self._current()
        return h.hexdigest()

def new(key, msg = None, digestmod = None):
    return HMAC(key, msg, digestmod)

def digest(key, msg = None, digestmod = None) -> bytes:
    return new(key, msg, digestmod).digest()


def test():
    resp = new(key=b'1234567890abcdef', msg=b'hello-message', digestmod=hashlib.sha256).digest()
    print(f'Test hmac: {resp}')
    assert(resp == bytes.fromhex('1e916164032c5006e6d8eb5024f8c98e6a365ea4d8a499999c978f9fd61e2e46'))
