#!/usr/bin/python3


import sys
import os
import unittest
import xmlrunner

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(path)
from test_tpl import test_tpl

class client_registration_test(test_tpl):
    def setUp(self):
        super().setUp()

    def test(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(),"out/tests")))
