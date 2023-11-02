#!/usr/bin/python3



import os
import unittest
import xmlrunner
import time


from test_tpl import test_tpl

class lifetime_test(test_tpl):

    def setUp(self):
        super().setUp()
        self.value = 0
        self.retv = 0
        self.rett = None
        self.status_tm = 0

    def on_status(self, t, v):
        self.rett = t
        self.retv = int(v)
        self.status_tm = time.time()

    def wait_status(self):
        print(f"Waiting for status: {self._uclient.lifetime + 1} s")
        self.rett = None
        self.wait_condition(lambda: self.rett is not None, self._uclient.lifetime + 1)

    
    def status(self):
        self.subscribe_hub('status', self.on_status)
        self.wait_status()
        pre = self.retv 
        start = self.status_tm
        print(f'Start: {start}')

        for i in range(30):
            self._device.set_reg(8, i)
            time.sleep(1)

        self.wait_status()
        print(f'Stop: {self.status_tm}; diff: {self.status_tm - start}')
        self.assertTrue((self.status_tm - start) >= (self._uclient.lifetime - 2))
        self.assertTrue(self.retv == (pre + i + 1))

    def test(self):
        self.status()
        self.publish_hub('lifetime',120)
        start = time.time()
        time.sleep(1)
        self.status()
        lifetime = (time.time() - start)
        print(f'Lifetime: {lifetime}')
        self.assertTrue(lifetime >= 118)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(), "out/tests")))
