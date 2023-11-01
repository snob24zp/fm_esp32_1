#!/usr/bin/python3



import os
import unittest
import xmlrunner
import version


from test_tpl import test_tpl

class ping_topic_test(test_tpl):

    def setUp(self):
        super().setUp()
        self.value = 0
        self.retv = 0
        self.rett = None

    def on_ver(self, t, v):
        self.rett = t
        self.retv = v


    def test(self):
        self.subscribe_hub('ping', self.on_ver)
        self.publish_hub('ping', 'ping')
        self.wait_condition(self.rett != 'ping', 10)
        self.assertTrue(self.retv == 'OK')


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(), "out/tests")))
