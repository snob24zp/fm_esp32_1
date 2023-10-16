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
from uclient.timedb import tbl_t

class event_device(mem_device):
    EVT_SZ = 512
    EVT_MAX_CNT = 64 
    EVT_PER_SEND = 4
    MEM_DIR = 'data'
    FNAME = '%d.evt'
    TBLNAME = '%d.tbl'
    FPATH = f'{MEM_DIR}/{FNAME}'
    TBLPATH = f'{MEM_DIR}/{FNAME}'

    def __init__(self, serial, dtype=device_base.DEVICE_TYPE, regs={}, status=0):
        super().__init__(serial, dtype, regs, status)
        self._dbs = {}

    def set_reg(self, reg, value):
        if not reg in self._dbs:
            self._dbs[reg] = tbl_t(f'{self.serial}.{reg}', event_device.EVT_SZ)

        self._dbs[reg].push(value)
        return super().set_reg(reg, value)

    def event_hnd(self, topic: str, msg: str):
        if topic.startswith('events'):
            reg = int(topic.split('/')[1])
            (_from, _to) = msg.split(';')
            if reg in self._dbs:
                evt = self._dbs[reg].search(int(_from), True)
                if evt is not None:
                    count = 1
                    buf = [{'ts': evt[1].tm, 'r': reg, 'v': evt[2]}]
                    idx = evt[0] + 1
                    evt = evt[1:]

                    while count < event_device.EVT_MAX_CNT and evt[0].tm < int(_to):
                        evt = self._dbs[reg].at(idx)
                        if evt[0] is None:
                            break

                        buf.append({'ts': evt[0].tm, 'r': reg, 'v': evt[1]})
                        if len(buf) >= event_device.EVT_PER_SEND:
                            self.pub_dev(topic, buf)
                            buf = []

                        count += 1
                        idx += 1
                    
                    if len(buf) > 0:
                        self.pub_dev(topic, buf)

                self.pub_dev(topic, {})
            return True

        return False


    def hnd_msg(self, topic, msg):
        if not self.event_hnd(topic, msg):
            return super().hnd_msg(topic, msg)


def test():
    import base64
    import random
    from uclient.hub import HUB

    try:
        from machine import unique_id
    except ImportError:
        import random

        def unique_id():
            return b'112233'

    dev = event_device(12345)
    token = unique_id().hex(":")

    cl = HUB("x.ks.ua:1883", token, [dev])
    cl.connect()
    
    pre_time = time.time()
    while True:
        cl.step()
        if time.time() > (pre_time + 15):
            rnd_b = bytes([ random.randrange(0xff) for _ in range(random.randrange(32)) ])
            dev.set_reg(8, {'rnd_a': random.randint(0,2**30), 'rnd_data': base64.b64encode(rnd_b).decode()})
            pre_time = time.time()

if __name__ == '__main__':
    test()
