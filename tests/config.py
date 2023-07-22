

import os
import sys

try:
    from tests.json_object import json_object
except ImportError:
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(path)
    from json_object import json_object


class config_t(json_object):
    DEFAULT_BROKER = {'host': 'x.ks.ua', 'port': 1883}  # broker address
    DEFAULT_TOKEN = '48:3f:da:55:07:5b'
    DEFAULT_SERIAL = 3996365522
    DEFAULT_USER = "admin@admin.com"
    DEFAULT_PASSWORD = "11223344"
    DEFAULT_LOG_SRV = {
        "host": "elastic.x.ks.ua",
        "user": "logs",
        "pwd": ""
    }
    DEFAULT_FW_FILE = './tests/dev_uclient_test.latest.uebf'
    DEFAULT_FW_CRYPT_KEY = "dWNsaWVudC10ZXN0LWRldg=="
    DEFAULT_ADD_HASH = '668c227dd753261970f6266048f14ee9630922b2ff523f7fd96dd0928a28f37b'

    def __init__(self, cfg_file="config.json"):

        self.cfg_file = cfg_file
        self.broker = self.DEFAULT_BROKER
        self.token = self.DEFAULT_TOKEN
        self.serial = self.DEFAULT_SERIAL
        self.user = self.DEFAULT_USER
        self.pwd = self.DEFAULT_PASSWORD
        self.add_hash = self.DEFAULT_ADD_HASH
        self.log_srv = self.DEFAULT_LOG_SRV
        self.fw_file = self.DEFAULT_FW_FILE
        self.fw_crypt = self.DEFAULT_FW_CRYPT_KEY

        if os.path.exists(cfg_file):
            with open(cfg_file, "rt") as c:
                super().__init__(c.read())
        else:
            super().__init__()
            self.save()

    def save(self):
        '''
        Save config file
        '''
        with open(self.cfg_file, "wt") as c:
            c.write(self.json())
