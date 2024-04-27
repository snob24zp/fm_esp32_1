try:
    from time import ticks_ms
except ImportError:
    import time
    def ticks_ms():
        return int(time.time() * 1000)

import struct
import base64
import json
from log import log
from uclient.hmac import HMAC as hmac
from uclient.user import user_base


try:
    from micropython import const
except ImportError:
    def const(ret):
        return ret


class device_base(log):
    DEVICE_TYPE = const(1)     # Device type

    def __init__(self, serial, dtype=DEVICE_TYPE, regs={}, status=0):
        log.__init__(self, f'DEV-{serial}')
        self.info(f'Device {serial} (type: {dtype})  has been created')
        self.serial = serial
        self.dtype = dtype
        self.status = 0
        self.reg_time = 0
        self.regs = regs
        self.status = status
        self.regs[0] = serial
        self._hub = None

    @log.dbg_wr
    def set_hub(self, hub):
        self._hub = hub

    def pub_dev(self, topic, value):
        if self._hub is not None:
            ret = json.dumps(value)
            if self._hub.pub(f'{self.serial}/{topic}', ret):
                self.status += 1

    def step(self):
        pass

    @log.dbg_wr
    def set_reg(self, reg, value):
        if reg not in self.regs or self.regs[reg] != value:
            self.regs[reg] = value
            self.pub_dev(reg, value)

    @log.dbg_wr
    def publish_status(self):
        self._hub.pub_hub(f'{self.serial}/status', self.status)

    @log.dbg_wr
    def register(self, tm):
        self.info(f'Device {self.serial} registration on the server @ {tm}')
        self.regs[1] = tm
        self._hub.subscribe_hub(f'{self.serial}/#',">")

    @log.dbg_wr
    def hnd_msg(self, topic, msg):
        if self.on_change_reg(topic, msg):
            return

    def on_change_reg(self, topic: str, msg: object):
        if self.isnumeric(topic) and int(topic) > 1:
            self.info(f'Set REG[{topic}] = {msg}')
            self.regs[int(topic)] = msg # msg
            return True
        return False

    @staticmethod
    def isnumeric(inp):
        return all([ x >= '0' and x <= '9' for x in inp ])

    @staticmethod
    def int2float(b):
        '''
        Преобразовывает число int в float iee754
        '''
        try:
            s = struct.pack('>L', b)
            return struct.unpack('>f', s)[0]
        except Exception:
            return 0

    @staticmethod
    def float2int(b):
        '''
        Преобразовывает число float iee754 в int
        '''
        try:
            s = struct.pack('>f', b)
            return struct.unpack('>L', s)[0]
        except Exception:
            return 0

    @staticmethod
    def sign_value(value, uhash):
        """
        Подписывает сообщение
        """
        sign = base64.b64encode(hmac.new(key=uhash, msg=str(value).encode('utf-8')).digest()).decode('utf-8')
        return f'{value}.{sign}'

    @staticmethod
    def from_dict(dev: dict):
        d = device_base(serial=dev['serial'], regs=dev['regs'], events=dev['events'], status=dev['status'] if 'status' in dev else 0, users=[])

        if 'users' in dev:
            for u in dev['users']:
                d.users.append(user_base.from_dict(u))

        for k, v in enumerate(d.regs):
            d.schem[k] = type(v).__name__
        return d

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)

        raise Exception(f'{key} is not found')

    def __setitem__(self, key, value):
        if hasattr(self, key):
            return setattr(self, key, value)

    def __delitem__(self, key):
        delattr(self, key)

    def __contains__(self, key):
        return hasattr(self, key)

    @log.dbg_wr
    def info_req(self):
        return {"s": self.serial, "t": self.dtype, "r": self.regs}

    def serialize(self):
        return {"regs": self.regs, "events": self.events, "status": self.status, "users": self.users}
