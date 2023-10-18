#!/usr/bin/python3


import base64
import string
import sys
import os
import time
import unittest
import xmlrunner
from config import config_t
import random
from uclient.userdev import user_device

try:
    from tests.test_tpl import test_tpl
    import tests.user_utils as uu
except ImportError:
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(path)
    from test_tpl import test_tpl
    import user_utils as uu


class user_add_test(test_tpl):

    def setUp(self):
        super().setUp(dtype=user_device, dargs={'device_id': base64.b64decode(config_t().device_id)})
        self.user_res = 0
        self.users = []

    def add_admin_user(self):
        self.add_user(self.cfg.user, self.cfg.pwd, key=self.cfg.device_id)
        self.logger.info('Admin user has been added')
        time.sleep(1)
    
    def add_30user(self):
        for i in range(30):
            self.add_user(self.gen_username(), self.gen_pwd())
        time.sleep(1)

    def add_without_perm_user(self):
        _usr = (self.gen_username(), self.gen_pwd())
        _usr = (_usr[0], _usr[1],  uu.create_key(_usr[0],_usr[1]))
        self.add_user(_usr[0], _usr[1], 0x02)
        _pass = True
        try:
            self.add_user(self.gen_username(), self.gen_pwd(), key = _usr[2])
            _pass = False
        except:
            pass

        self.assertTrue(_pass)

    def add_more_than_max(self):
        _pass = True
        try:
            self.add_user(self.gen_username(), self.gen_pwd())
            _pass = False
        except:
            pass

        self.assertTrue(_pass)


    def test(self):
        self.add_admin_user()

        self.add_without_perm_user()
        self.add_30user()
        self.add_more_than_max()



if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(), "out/tests")))
