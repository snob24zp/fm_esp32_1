#!/usr/bin/python3

import json
import sys
import os
import unittest
import xmlrunner

try:
    from tests.test_tpl import test_tpl
except ImportError:
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(path)
    from test_tpl import test_tpl


class user_list_test(test_tpl):

    def setUp(self):
        super().setUp()
        self.users = []
        self.user_recv_done = False
        self.subscribe_device('user/list', self.on_list)

    def on_list(self, topic, value):
        self.logger.info(f"list response: ({topic}) {value}")
        u = json.loads(value)
        if "u" in u and "p" in u and "n" in u and self.user_recv_done == False:
            self.users.append(u)
        else:
            self.user_recv_done = True

    def test(self):
        self.publish_device('user/list', 'list', self.cfg.user_key)
        self.wait_condition(lambda: self.users is not None, 30)
        self.wait_condition(lambda: self.user_recv_done, 30)
        for user in self.users:
            self.logger.info(f'===> Got: hash: {user["u"]} ; p: {user["p"]}, name: {user["n"]}')


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(),"out/tests")))
