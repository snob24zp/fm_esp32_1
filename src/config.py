from micropython import const
from json_object import json_object
import os
from machine import unique_id

_filename = const('config.json')

class config_t(json_object):
    def __init__(self, cfg_file = _filename):
        self.wlan_mode = 1 # ap
        self.ap_ssid = f'AR-{unique_id().hex()}'
        self.ap_pwd = ''
        self.sta_ssid = f'AR-{unique_id().hex()}'
        self.sta_pwd = f'12345678'
        self.ifconfig = ('dhcp',)
        self.server = "mqtt://x.ks.ua"
        self.token = unique_id().hex(':')

        if cfg_file in os.listdir('.'):
            with open(cfg_file, "rt") as c:
                super().__init__(c.read())
        else:
            super().__init__()

    def save(self, cfg_file = _filename):
        '''
        Save config file
        '''
        with open(cfg_file, "wt") as c:
            c.write(self.json())
