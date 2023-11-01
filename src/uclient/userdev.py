import os
import base64
import struct

import json
import hashlib
try:
    from time import ticks_ms
except ImportError:
    import time

    def ticks_ms():
        return int(time.time() * 1000)

from uclient.device import device_base
import uclient.aes as aes
import uclient.hmac as hmac
from config import config_t

class user:
    MEM_DIR = 'data'
    FNAME = f'acl.json'
    FPATH = f'{MEM_DIR}/{FNAME}'

    FMT = '>32sB64shx'
    ACL_FMT = '>h{cnt}'
    def __init__(self, uid, perm, name, acl_idx) -> None:
        self.uid = uid
        self.perm = perm
        self.name = name
        self.acl = self.load_acl(acl_idx)

    @staticmethod
    def load_acl(idx: int) -> list:
        if idx >= 0 and user.FNAME in os.listdir(f'./{user_device.MEM_DIR}'):
            with open(user.FPATH, 'rt') as fd:
                return json.load(fd)[idx]
        return []

    @staticmethod
    def save_acl(acl: list) -> int:
        if len(acl) == 0:
            return -1

        _acls = []
        if user.FNAME in os.listdir(f'./{user_device.MEM_DIR}'):
            with open(user.FPATH, 'rt') as fd:
                _acls = json.load(fd)
                for idx, itm in enumerate(_acls):
                    if list(acl) == itm:
                        return idx
                
        _acls.append(acl)
        with open(user.FPATH, 'wt') as fd:
            json.dump(_acls, fd)

        return len(_acls) - 1


    @staticmethod
    def parse(data):
        return user(*struct.unpack(user.FMT, data))
    
    def serialize(self):
        acl_offset = user.save_acl(self.acl)
        return struct.pack(user.FMT, self.uid, self.perm, self.name, acl_offset)
    
    def __str__(self) -> str:
        name = self.name.strip(b'\0').decode()
        return f'{name} ({self.uid.hex()})'
    
    def __repr__(self) -> str:
        return self.__str__()

class user_device(device_base):
    MEM_DIR = 'data'
    FNAME = f'%d.users'
    FPATH = f'{MEM_DIR}/{FNAME}'
    ADD_FMT = '>32sB64s'
    MAX_USER_CNT = 32
    
    PERM_REG_WR = 0x02
    PERM_MEM_RD = 0x04
    PERM_MEM_WR = 0x08
    PERM_FWUPD  = 0x10
    PERM_EVENTS = 0x20
    PERM_USERS  = 0x40
    PERM_F_RES  = 0x80

    def __init__(self,  serial: int, dtype=device_base.DEVICE_TYPE, regs={}, status=0, device_id: bytes = None):
        
            
        super().__init__(serial, dtype, regs, status)
        self._device_id = bytes.fromhex(config_t().device_id) if device_id is None else device_id
        if not user_device.MEM_DIR in os.listdir('.'):
            os.mkdir(user_device.MEM_DIR)
 
        self.__user_list = user_device.load_db(serial)
    
    def set_hub(self, hub):
        super().set_hub(hub)
        self._hub.register_root_cb('>user/dev',self.on_user_dev)

    @staticmethod
    def load_db(serial):
        _fname = user_device.FPATH % serial
        _fpath = user_device.FPATH % serial
        ret = []
        if _fname in os.listdir(f'./{user_device.MEM_DIR}'):
            with open(_fpath, 'rb') as fd:
                while True:
                    usr = fd.read(struct.calcsize(user_device.USR_STRUCT))
                    if not usr:
                        break
                    ret.append(user.parse(usr))
        return ret

    @staticmethod
    def save_db(serial, user_list):
        _fpath = user_device.FPATH % serial
        with open(_fpath, 'wb') as fd:
            for usr in user_list:
                fd.write(usr.serialize())

    def check_sign(self, msg: str):
        if len(self.__user_list) > 0:
            (msg, imac) = msg.split('.')
            for usr in self.__user_list:
                cmac = hmac.digest(usr.uid, msg.encode(), hashlib.sha256)
                if base64.b64decode(imac) == cmac:
                    return msg, usr
            return None, None
        return msg, None

    def sign_message(self, msg):
        if isinstance(msg, str):
            msg = msg.encode()

        msg = base64.b64encode(msg)
        sig = base64.b64encode(hmac.new(self._device_id, msg, hashlib.sha256).digest()).decode()
        return f'{msg.decode()}.{sig}'

    def on_user_add(self, topic, msg, usr):
        if topic == 'user/add':
            #1. decipher text
            #2. unpack via struct
            #3. apply to user_list
            
            if len(self.__user_list) >= user_device.MAX_USER_CNT:
                self.err('Maximum user count is reached')
                return True

            key = self._device_id
            if usr is None and len(self.__user_list) > 0:
                self.err('Unknown user tries to add new user')
                return True
            elif usr is not None:
                key = usr.uid

            if  usr is not None and (usr.perm & user_device.PERM_USERS) == 0:
                self.err(f'User ({usr.name.decode()}) don\'t have permission to add new users')
                return True

            sz = struct.calcsize(user_device.ADD_FMT)
            if len(msg) < sz:
                return True

            msg = aes.decrypt(base64.b64decode(msg), key)
            (uid, perm, name) = struct.unpack(user_device.ADD_FMT, msg[:sz])
            for idx, _usr in enumerate(self.__user_list):
                if _usr.name == name or _usr.uid == uid:
                    self.__user_list.remove(_usr)
                    break
                    #return True

            acls = struct.unpack(f'>{(len(msg) - sz)//2}h', msg[sz:])
            self.__user_list.append(user(uid, perm, name, user.save_acl(acls)))
            user_device.save_db(self.serial, self.__user_list)
            self.pub_dev(topic, aes.encrypt('"OK"'.encode(), self._device_id))
            return True
        return False

    def on_user_list(self, topic, msg, usr):
        if topic == 'user/list':
            if usr is None:
                self.err('User auth failed')
                return True

            if (usr.perm & user_device.PERM_USERS) == 0:
                self.err(f'User ({usr.name}) don\'t have permission to add new users')
                return True


            msg = aes.decrypt(base64.b64decode(msg), usr.uid).decode()
            if msg == 'list':
                for _usr in self.__user_list:
                    ret = {'u': base64.b64encode(_usr.uid).decode(), 'n': _usr.name.strip(b'\0').decode(), 'p': _usr.perm, 'a': _usr.acl }
                    self.pub_dev(topic, aes.encrypt(json.dumps(ret).encode(), usr.uid))
                self.pub_dev(topic, aes.encrypt(json.dumps({}).encode(), usr.uid))
        return False

    def on_user_remove(self, topic, msg, usr):
        if topic == 'user/remove':
            if usr is None:
                self.err('User auth failed')
                return True
            
            if (usr.perm & user_device.PERM_USERS) == 0:
                self.err(f"User ({usr}) don\'t have permission to remove users")
                return True

            uid = aes.decrypt(base64.b64decode(msg), usr.uid)

            if usr.uid == uid:
                self.err('User can\'t remove himself')
                return True
            
            for _usr in self.__user_list:
                if _usr.uid == uid:
                    self.__user_list.remove(_usr)
                    self.pub_dev(topic, aes.encrypt('"OK"'.encode(), usr.uid))
                    break
            return True

        return False
    
    def on_user_dev(self, topic,  msg):
        # on root topic ('>user/dev')
        for _usr in self.__user_list:
            if base64.b64decode(msg) == hashlib.sha256(_usr.uid).digest():
                self._hub.client.publish("<user/dev", f"{self._hub.token}/{self.serial}", qos=1)
                break

    def pub_dev(self, topic, value):
        if len(self.__user_list) > 0:
            value = self.sign_message(value)

        return super().pub_dev(topic, value)

    def hnd_msg(self, topic, msg):
        (msg, usr) = self.check_sign(msg)

        if msg is not None:
            if self.on_user_add(topic, msg, usr):
                return
            if self.on_user_list(topic, msg, usr):
                return
            if self.on_user_remove(topic, msg, usr):
                return

            return super().hnd_msg(topic, msg)


def test():
    from uclient.hub import HUB

    try:
        from machine import unique_id
    except ImportError:
        from config import config_t

        def unique_id():
            return config_t().mac
    
    device_id = hashlib.sha256('device'.encode()).digest()
    dev = user_device(device_id, 12345)
    token = unique_id().hex(":")

    cl = HUB("x.ks.ua:1883", token, [dev])
    cl.connect()

    while True:
        cl.step()


if __name__ == '__main__':
    test()
