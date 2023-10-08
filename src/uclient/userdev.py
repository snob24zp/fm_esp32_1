import os
import base64

try:
    from time import ticks_ms
except ImportError:
    import time

    def ticks_ms():
        return int(time.time() * 1000)

from uclient.device import device_base


class user_device(device_base):
    MEM_SZ = 1024
    MEM_DIR = 'data'
    FNAME = f'%d.bin'
    FPATH = f'{MEM_DIR}/{FNAME}'

    def __init__(self, serial, dtype=device_base.DEVICE_TYPE, regs={}, status=0):
        super().__init__(serial, dtype, regs, status)
        self.pre_time = ticks_ms()
        self.__fname = user_device.FNAME % serial
        self.__fpath = user_device.FPATH % serial

        if not user_device.MEM_DIR in os.listdir('.'):
            os.mkdir(user_device.MEM_DIR)

        if not self.__fname in os.listdir(f'./{mem_device.MEM_DIR}'):
            with open(self.__fpath, 'wb') as fd:
                fd.write(bytearray([0xff] * mem_device.MEM_SZ))
                fd.flush()

    def user_add(self, name, )

    def hnd_msg(self, topic, msg):
        if self.on_mem_read(topic, msg):
            return
        if self.on_mem_write(topic, msg):
            return

        return super().hnd_msg(topic, msg)

    def on_mem_read(self, topic, value):
        if topic == 'read':
            (addr, sz) = str(value).split(';')
            self.info(f'Reading memory: @{addr}[{sz}]')
            try:
                data = self.read_mem(int(addr), int(sz))
                if data is not None:
                    self.pub_dev(topic, f'{len(data)};{base64.b64encode(data).decode()}', True)
            except Exception as ex:
                self.err('read-mem exception', ex)
        
            return True
        return False

    def on_mem_write(self, topic, value):
        if topic == 'write':
            (addr, data) = value.split(';')
            data = base64.b64decode(data)  # test if put wrong b64 data
            self.pub_dev(topic, f'{addr};{self.write_mem(int(addr), data)}', True)
            return True
        return False


def test():
    from uclient.hub import HUB

    try:
        from machine import unique_id
    except ImportError:
        import random

        def unique_id():
            return random.randbytes(6)

    dev = mem_device(12345)
    token = unique_id().hex(":")

    # sha256("ap0\0y78bug57\0")
    # add_hash = "668c227dd753261970f6266048f14ee9630922b2ff523f7fd96dd0928a28f37b"

    cl = HUB("x.ks.ua:1883", token, [dev])
    cl.connect()

    while True:
        cl.step()


if __name__ == '__main__':
    test()
