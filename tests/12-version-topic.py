#!/usr/bin/python3



import os
import unittest
import xmlrunner
import version


from test_tpl import test_tpl

class version_topic_test(test_tpl):

    def setUp(self):
        super().setUp()
        self.value = 0
        self.retv = 0
        self.rett = None

    def on_ver(self, t, v):
        self.rett = t
        self.retv = v

    def test(self):
        self.subscribe_hub('version', self.on_ver)
        self.publish_hub('version', 'version')
        self.wait_condition(self.rett != 'version', 10)
        self.assertTrue(self.retv == version.STATIC_VERSION)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(), "out/tests")))
