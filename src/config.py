
from json_object import json_object
import os

import sys
if sys.version.count('MicroPython') > 0:
    from machine import unique_id
    _filename = 'config.json'
else:
    _filename = 'simu-cfg.json'

    def unique_id():
        return os.urandom(6)

class config_t(json_object):
    def __init__(self, cfg_file = _filename):
        self.mac = unique_id().hex()
        self.wlan_mode = 1 # ap
        self.ap_ssid = f'AR-{self.mac}'
        self.ap_pwd = ''
        self.sta_ssid = f'AR-{self.mac}'
        self.sta_pwd = f'12345678'
        self.ifconfig = ('dhcp',)
        self.server = "x.ks.ua"
        self.token = bytes.fromhex(self.mac).hex(':')
        self.serial = int.from_bytes(bytes.fromhex(self.mac)[2:],'little')

        if cfg_file in os.listdir('.'):
            with open(cfg_file, "rt") as c:
                super().__init__(c.read())
        else:
            super().__init__()
            self.save()

    def save(self, cfg_file = _filename):
        '''
        Save config file
        '''
        with open(cfg_file, "wt") as c:
            c.write(self.json())
