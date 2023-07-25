import os
import json
import struct

try:
    from time import ticks_ms
except ImportError:
    import time

    def ticks_ms():
        return int(time.time() * 1000)

from uclient.device import device_base
from uclient.memdev import mem_device


class event_device(mem_device):
    EVT_SZ = 16384
    MEM_DIR = 'data'
    FNAME = f'%d.evt'
    FPATH = f'{MEM_DIR}/{FNAME}'

    class event_t:
        EVT_FMT = '>LLLH'
        def __init__(self, reg: int, value:object) -> None:
            self.tm = int(time.time())
            self.r = reg
            self.v = value
            
        @staticmethod
        def parse(raw: bytes):
            bg = struct.calcsize(event_device.event_t.EVT_FMT)
            (r, tm, dsz) = struct.unpack(event_device.event_t.EVT_FMT, raw[:bg])
            data = raw[bg:bg+dsz]
            evt = event_device.event_t(r, json.loads(data))
            evt.tm = tm
            return evt

        def serialize(self):
            data = json.dumps(self.v).encode()
            ret = bytearray()
            ret.extend(struct.pack(event_device.event_t.EVT_FMT, self.r, self.tm,len(data))) # reg;time;data-sz;data
            ret.extend(data)
            return ret
        
        def __repr__(self) -> str:
            return f'Event@{self.tm} [[{self.r}] = {self.v}]'
        
        def __str__(self) -> str:
            return self.__repr__()

    def __init__(self, serial, dtype=device_base.DEVICE_TYPE, regs={}, status=0):
        super().__init__(serial, dtype, regs, status)
        self.pre_time = ticks_ms()
        self.__fpath = mem_device.FPATH % serial

        if not mem_device.MEM_DIR in os.listdir('.'):
            os.mkdir(mem_device.MEM_DIR)

    def push_evt(self, evt: event_t) -> int:
        sz = os.stat(self.__fpath)[6]


        with open(self.__fpath, 'r+b') as fd:
            fd.seek(addr, 0)
            return fd.write(data)

    def read_mem(self, addr: int, sz: int) -> bytes:
        if sz > 1024:
            return

        fsz = os.stat(self.__fpath)[6]
        if addr < fsz:
            if (addr + sz) > fsz:
                sz = fsz - addr
                self.warn(f'Response has been truncated to: {sz}')

            with open(self.__fpath, 'rb') as fd:
                fd.seek(addr, 0)
                return fd.read(sz)
        else:
            self.warn('Position out of file')

        return None

    def hnd_msg(self, topic, msg):
        if self.on_mem_read(topic, msg):
            return
        if self.on_mem_write(topic, msg):
            return

        return super().hnd_msg(topic, msg)

def evt_test():
    evt = event_device.event_t(160, {'obj-a': {'str-type': 'str', 'int': 1234, 'float': 12.345}, 'list': [1,2,3,4,5]})
    print(f'Created {evt} -> {evt.serialize().hex()}')
    bs = evt.serialize()
    ret = event_device.event_t.parse(bs)
    print(f'Parsed {ret}, len: {len(bs)}')
    assert(ret.r == evt.r)
    assert(ret.tm == evt.tm)
    assert(ret.v == evt.v)

    evt = event_device.event_t(170, 431.123)
    print(f'Created {evt} -> {evt.serialize().hex()}')
    bs = evt.serialize()
    ret = event_device.event_t.parse(bs)
    print(f'Parsed {ret}, len: {len(bs)}')
    assert(ret.r == evt.r)
    assert(ret.tm == evt.tm)
    assert(ret.v == evt.v)


def test():
    from uclient.hub import HUB

    try:
        from machine import unique_id
    except ImportError:
        import random

        def unique_id():
            return random.randbytes(6)

    dev = event_device(12345)
    token = unique_id().hex(":")

    # sha256("ap0\0y78bug57\0")
    # add_hash = "668c227dd753261970f6266048f14ee9630922b2ff523f7fd96dd0928a28f37b"

    cl = HUB("x.ks.ua:1883", token, [dev])
    cl.connect()

    while True:
        cl.step()


if __name__ == '__main__':
    evt_test()
