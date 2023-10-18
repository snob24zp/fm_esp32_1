#!/usr/bin/python3


import sys
import os
import unittest
import xmlrunner
import base64

from config import config_t
from uclient.userdev import user_device
try:
    from tests.test_tpl import test_tpl
except ImportError:
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(path)
    from test_tpl import test_tpl


class user_list_test(test_tpl):

    def setUp(self):
        super().setUp(skip_add_user = False, dtype=user_device, dargs={'device_id': base64.b64decode(config_t().device_id)})
        self.users = []
        self._income_users = []
        self.user_recv_done = False
        self.subscribe_device('user/list', self.on_list)

    def add_31user(self):
        for i in range(31):
            self.users.append((self.gen_username(), self.gen_pwd()))
            self.add_user(*self.users[-1])

    def on_list(self, topic, value):
        self.logger.info(f"list response: ({topic}) {value}")
        self.user_recv_done = True
        self._income_users.append(value)

    def send_list_cmd(self):
        self.subscribe_device_encrypted('user/list', self.on_list, self.cfg.user_key)
        self.publish_device_encrypted('user/list', 'list')
        self.wait_condition(lambda: self.user_recv_done, 30)


    def test(self):
        self.add_31user()
        self.send_list_cmd()
        for user in self._income_users:
            for _usr in self.users:
                if user['n'] == _usr[0]:
                    self.users.remove(_usr)
                    self.logger.info(f'===> Got: hash: {user["u"]} ; p: {user["p"]}, name: {user["n"]}')
                    break

        self.assertTrue(len(self.users) == 0)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(),"out/tests")))
