"""
Device configuration file
"""

import os
import hashlib
import sys

from json_object import json_object

if sys.version.count('MicroPython') > 0:
    from machine import reset
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
        self.sta_pwd = '12345678'
        self.ifconfig = ('dhcp',)
        self.server = "x.ks.ua"
        self.token = bytes.fromhex(self.mac).hex(':')
        self.serial = int.from_bytes(bytes.fromhex(self.mac)[2:],'little')
        self.device_id = hashlib.sha256(self.mac.encode()).digest().hex()
        self.force_wlan = False
        self.srv_user = ""
        self.srv_pwd = ""

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

    def reset(self, cfg_file = _filename):
        os.unlink(cfg_file)
        if sys.version.count('MicroPython') > 0:
            reset()
