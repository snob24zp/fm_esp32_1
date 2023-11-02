#!/usr/bin/python3



import sys
import os
import time
import random
import unittest
import xmlrunner
import json

from test_tpl import test_tpl

class reg_value_exchange_test(test_tpl):

    def setUp(self):
        super().setUp()
        self.value = 0
        self.retv = 0
        self.rett = None

    def on_chg_reg(self, t, v):
        self.rett = t
        self.retv = v

    def srv_side(self):
        self.value = random.randint(0, 65535)
        self.logger.info(f'------- 1. Set register 8 to value {self.value} from server side')
        self.publish_device('8', self.value)
        self.wait_condition(lambda: 8 in self._device.regs, 10)
        self.assertTrue(self._device.regs[8] == self.value)

    def cl_side(self):
        self.value = random.randint(0, 65535)
        self.logger.info(f'------- 2. Set register 8 to value {self.value} from device side')
        self.subscribe_device('8', self.on_chg_reg)
        self._device.set_reg(8, self.value)
        self.rett = None
        self.wait_condition(lambda: self.rett is not None, 10)
        self.assertTrue(self.rett == '8')
        self.assertTrue(self.value == int(self.retv))
        
    def srv_non_int_msg(self):
        self.value = {'rnd-a': random.randint(0, 65535), 'rnd-b': random.randint(0, 65535) }
        self.logger.info(f'------- 3. Set register 9 to value {self.value} from server side')
        self.publish_device('9', self.value)
        self.wait_condition(lambda: 9 in self._device.regs, 10)
        self.assertTrue(self._device.regs[9] == self.value)
        
    def cl_non_int_msg(self):
        self.value = {'rnd-a': random.randint(0, 65535), 'rnd-b': random.randint(0, 65535) }
        self.logger.info(f'------- 4. Set register 9 to value {self.value} from device side')
        self.subscribe_device('9', self.on_chg_reg)
        self._device.set_reg(9, self.value)
        self.rett = None
        self.wait_condition(lambda: self.rett is not None, 10)
        self.assertTrue(self.rett == '9')
        self.assertTrue(self.value == self.retv)

    def test(self):
        self.srv_side()
        time.sleep(1)
        self.cl_side()
        time.sleep(1)
        self.srv_non_int_msg()
        time.sleep(1)
        self.cl_non_int_msg()


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(), "out/tests")))
