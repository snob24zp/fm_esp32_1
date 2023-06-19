from micropython import const
from json_object import json_object
import os

_filename = const('config.json')

class config_t(json_object):
    
    def __init__(self, cfg_file = _filename):
        self.servo_cal = [
            0,0,0,0,0,0,0
        ]

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
