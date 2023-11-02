#!/usr/bin/python3


import os
import base64
import time
import random
import unittest
import xmlrunner

from test_tpl import test_tpl

class memops_test(test_tpl):

    def setUp(self):
        super().setUp()
        self.topic = None
        self.value = None

    def on_resp(self, topic: str, value: str):
        self.value = value
        self.topic = topic

    def read_mem(self):
        data = random.randbytes(64)
        self._device.write_mem(32,data)
        self.subscribe_device('read', self.on_resp)
        self.topic = None
        self.publish_device('read','32;64')
        self.wait_condition(lambda: self.topic is not None, 10)
        self.assertTrue(self.topic == 'read')
        (sz, ret) = self.value.split(';')
        self.assertTrue(int(sz) == 64)
        self.assertTrue(data == base64.b64decode(ret))

    def write_mem(self):
        data = random.randbytes(64)
        self.subscribe_device('write', self.on_resp)
        self.topic = None
        self.publish_device('write',f'32;{base64.b64encode(data).decode()}')
        self.wait_condition(lambda: self.topic is not None, 10)
        self.assertTrue(self.topic == 'write')
        (addr, sz) = self.value.split(';')
        self.assertTrue(int(addr) == 32)
        self.assertTrue(int(sz) == 64)

        ddata = self._device.read_mem(32, 64)
        self.assertTrue(data == ddata)

    def test(self):
        self.read_mem()
        time.sleep(1)
        self.write_mem()



if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(), "out/tests")))
