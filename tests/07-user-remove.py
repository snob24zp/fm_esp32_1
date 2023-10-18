#!/usr/bin/python3

import random
import sys
import os
import unittest
import xmlrunner
import time
import base64

try:
    from tests.test_tpl import test_tpl
    import tests.user_utils as uu
except ImportError:
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(path)
    from test_tpl import test_tpl
    import user_utils as uu


class user_remove_test(test_tpl):

    def setUp(self):
        super().setUp()
        self.user_res = None
        self.subscribe_device_encrypted('user/remove', self.on_evt)
        self.user_res = None

    def on_evt(self, topic, value):
        self.user_res = value

    def unknown_user_rm(self):
        self.logger.info("##### Unknown user remove test #####")
        self.user_res = None
        self.publish_device_encrypted('user/remove', base64.b64encode(os.urandom(32)).decode('utf-8'), self.cfg.user_key)
        time.sleep(30)
        self.assertTrue(self.user_res == None)
        self.logger.info("Error was returned as planned")

    def known_user_rm(self):
        self.logger.info("##### Known user remove test #####")
        _usr = (self.gen_username(), self.gen_pwd())
        _usr = (_usr[0], _usr[1],  uu.create_key(_usr[0],_usr[1]))
        self.add_user(_usr[0], _usr[1], 0x02)

        self.user_res = None
        uid_b64 = base64.b64encode(_usr[2]).decode('utf-8')
        self.publish_device_encrypted('user/remove', uid_b64, self.cfg.user_key)
        self.wait_condition(lambda: self.user_res != None, 60)
        self.logger.info("User removed. Good")

    # def known_user_wo_perm_rm(self):
    #     self.logger.info("##### Known user remove without permissions test #####")
    #     (_, user_id) = self.add_user('remov2@known.user', '2', 0x3f)
    #     (_, rm_id) = self.add_user('remov3@known.user', '3', 0xff)
    #     time.sleep(5)
    #     self.user_res = None
    #     uid_b64 = base64.b64encode(rm_id).decode('utf-8')
    #     self.publish_device('user/remove', uid_b64, user_id)
    #     time.sleep(10)
    #     self.assertTrue(self.user_res == None)
    #     self.logger.info("Error was returned as planned")

    # def myself_rm(self):
    #     self.logger.info("##### Removing myself test #####")
    #     self.user_res = None
    #     uid_b64 = base64.b64encode(self.cfg.user_key).decode('utf-8')
    #     self.publish_device('user/remove', uid_b64, self.cfg.user_key)
    #     self.wait_condition(lambda: self.user_res == -1, 60)
    #     self.logger.info("Error was returned as planned")

    def test(self):
        self.unknown_user_rm()
        self.known_user_rm()
        
        # time.sleep(10)
        # self.known_user_wo_perm_rm()
        # time.sleep(10)
        # self.myself_rm()

if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(),"out/tests")))
