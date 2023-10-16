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
import uclient.aes as aes
from uclient.userdev import user_device, user

try:
    from tests.test_tpl import test_tpl
    import tests.user_utils as uu
except ImportError:
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(path)
    from test_tpl import test_tpl
    import user_utils as uu


class user_add_test(test_tpl):
    ADJECTIVES = ['Affable', 'Agreeable', 'Amiable', 'Charming', 'Polite',
                  'Likeable', 'Gregarious', 'Considerate', 'Sympathetic', 'Understanding']
    NAMES = ['James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer',
             'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Barbara']
    MAIL_HOSTS = ['gmail.com', 'x.ks.ua', 'dlab.pw', 'hotmail.com',
                  'outlook.com', 'vegaiot.com', 'i.ua', 'tlc.ks.ua']

    def setUp(self):
        super().setUp(dtype=user_device, dargs={'device_id': base64.b64decode(config_t().device_id)})
        self.user_res = 0
        self.users = []

    def gen_pwd(self, pwd_len=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=pwd_len))

    def gen_username(self):
        return f"{random.choice(self.ADJECTIVES).lower()}.{random.choice(self.NAMES).lower()}@{random.choice(self.MAIL_HOSTS)}"

    def add_admin_user(self):
        self.add_user(self.cfg.user, self.cfg.pwd, key=self.cfg.device_id)
        self.logger.info('Admin user has been added')
        time.sleep(1)
    
    def add_32user(self):
        for i in range(32):
            self.add_user(self.gen_username(), self.gen_pwd())
        time.sleep(1)

    def test(self):
        self.add_admin_user()
        self.add_32user()
        try:
            self.add_admin_user()
            self.assertTrue(False)
        except:
            pass

        # self.add_wrong_namelen_user()
        # time.sleep(10)
        # self.add_with_null_perm_user()
        # time.sleep(10)
        # self.add_without_perm_user()


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(), "out/tests")))
