#!/usr/bin/python3



import os
import unittest
import xmlrunner
import time


from test_tpl import test_tpl

class hub_topic_test(test_tpl):

    def setUp(self):
        super().setUp()
        self.retv = None

    def on_dev_found(self, t, v):
        self.rett = t
        self.retv = v

    def test(self):
        self.subscribe('<hub', self.on_dev_found)
        self.publish('>hub', f'{self._device.serial}')
        self.wait_condition(lambda: self.retv != f'{self._uclient.token}', 30)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(), "out/tests")))
