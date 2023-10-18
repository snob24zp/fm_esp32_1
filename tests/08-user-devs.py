#!/usr/bin/python3

import base64
import json
import sys
import os
import unittest
import hashlib
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
        self.devs = []
        self.user_recv_done = False
        self.subscribe('/user/dev', self.on_list_dev)
        self.uid_hash = None

    def on_list_dev(self, topic, value):
        if value != self.uid_hash:
            self.devs.append(value)

    def test(self):
        self.uid_hash = hashlib.sha256(self.cfg.user_key).digest()
        self.uid_hash = base64.b64encode(self.uid_hash).decode('utf-8')
        self.logger.info(f'User-ID hash: {self.uid_hash}')
        self.publish('/user/dev', self.uid_hash)
        self.wait_condition(lambda: len(self.devs) > 0, 30)
        for dev in self.devs:
            self.logger.info(f'===> Found device: {dev}')


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(),"out/tests")))
