#!/usr/bin/python3


import time
import os
import unittest
import xmlrunner


from test_tpl import test_tpl

class last_will_test(test_tpl):

    def setUp(self):
        super().setUp()
        self._status = None

    def on_status(self, topic, value):
        self._status = int(value)

    def test(self):
        self.subscribe_hub("status", self.on_status)
        self._uclient.client.client.sock.close() # unexpected close the socket for last will
        self.wait_condition(lambda: self._status == -1, 70)
        
    def tearDown(self) -> None:
        self.__running = False
        self.client.disconnect()



if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(), "out/tests")))
