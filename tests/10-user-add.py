#!/usr/bin/python3

import json
import string
import time
import random
import sys
import os
import unittest
import base64
import xmlrunner

try:
    from tests.test_tpl import test_tpl
    import tests.user_utils as uu
except ImportError:
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(path)
    from test_tpl import test_tpl
    import user_utils as uu


class user_add_test(test_tpl):
    ADJECTIVES = ['Affable', 'Agreeable', 'Amiable', 'Charming', 'Polite',
                  'Likeable', 'Gregarious', 'Considerate', 'Sympathetic', 'Understanding']
    NAMES = ['James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer',
             'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Barbara']
    MAIL_HOSTS = ['gmail.com', 'x.ks.ua', 'dlab.pw', 'hotmail.com',
                  'outlook.com', 'vegaiot.com', 'i.ua', 'tlc.ks.ua']

    def setUp(self):
        super().setUp()
        self.user_res = 0
        self.users = []

    def on_add(self, topic, value):
        user_res = int(value)
        if (user_res == -1):
            self.logger.error("Error creating user")
            self.user_res = None
            return
        self.user_res = user_res

    def on_add_existed(self, topic, value):
        self.user_res = int(value)

    def gen_pwd(self, pwd_len=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=pwd_len))

    def gen_username(self):
        return f"{random.choice(self.ADJECTIVES).lower()}.{random.choice(self.NAMES).lower()}@{random.choice(self.MAIL_HOSTS)}"

    def add_users(self, count = 16):
        self.logger.info('#####  Add users test #####')
        self.subscribe_device('user/add', self.on_add)
        for i in range(count):
            username = self.gen_username()
            pwd = self.gen_pwd()
                
            user_id = uu.create_key(username, pwd)
            self.logger.info(f"Create user: {username} pwd: {pwd} user_id: {user_id.hex()}")

            uid_b64 = base64.b64encode(user_id).decode('utf-8')
            cu_b64 = uu.create_user(user_id, 255, username)

            self.users.append({'u': uid_b64, 'p': 255, 'n': username})
            self.user_res = None
            self.publish_device('user/add', cu_b64.decode('utf-8'), self.cfg.user_key)
            self.wait_condition(lambda: self.user_res != None, 60)
            self.logger.info(f"User created with: {self.user_res} position", )
            time.sleep(0.5)

    def add_existed_user(self):
        self.logger.info('#####  Add existed user test #####')
        self.subscribe_device('user/add', self.on_add_existed)
        user = random.choice(self.users)
        self.logger.info(f'Add existed user: {user}')
        self.user_res = None
        self.publish_device('user/add', uu.create_user(base64.b64decode(user['u']), user['p'], user['n']).decode('utf-8'), self.cfg.user_key)
        self.wait_condition(lambda: self.user_res == -1, 60)
        self.logger.info("Error was returned as planned")

    def add_wrong_namelen_user(self):
        self.logger.info('#####  Add user with wrong name len test #####')
        self.subscribe_device('user/add', self.on_add_existed)
        
        username = self.gen_username()
        pwd = self.gen_pwd()
        user_id = uu.create_key(username, pwd)
        self.logger.info(f"Create user: {username} pwd: {pwd} user_id: {user_id.hex()}")

        self.user_res = None
        u = uu.create_user(user_id, 255, username)
        u = bytearray(base64.b64decode(u))
        u[33] = 127
        self.publish_device('user/add', base64.b64encode(u).decode('utf-8'), self.cfg.user_key)
        self.wait_condition(lambda: self.user_res == -1, 60)
        self.logger.info("Error was returned as planned")

    def add_with_null_perm_user(self):
        self.logger.info('#####  Add user with nulled permissions test #####')
        self.subscribe_device('user/add', self.on_add_existed)
        username = self.gen_username()
        pwd = self.gen_pwd()
        user_id = uu.create_key(username, pwd)
        self.logger.info(f"Create user: {username} pwd: {pwd} user_id: {user_id.hex()}")
        
        self.user_res = None
        u = uu.create_user(user_id, 0, username)
        self.publish_device('user/add', u.decode('utf-8'), self.cfg.user_key)
        self.wait_condition(lambda: self.user_res == -1, 60)
        self.logger.info("Error was returned as planned")

    def add_without_perm_user(self):
        self.logger.info('#####  Add user without permissions test #####')
        self.subscribe_device('user/add', self.on_add)
        username = self.gen_username()
        pwd = self.gen_pwd()
        user_id = uu.create_key(username, pwd)
        self.logger.info(f"Create user: {username} pwd: {pwd} user_id: {user_id.hex()}")
        self.user_res = None
        u = uu.create_user(user_id, 0x3f, username)
        self.publish_device('user/add', u.decode('utf-8'), self.cfg.user_key)
        self.wait_condition(lambda: self.user_res != None, 60)
        self.logger.info(f"User without permission added {self.user_res}")
        
        time.sleep(2)
        
        self.subscribe_device('user/add', self.on_add_existed)
        username = self.gen_username()
        pwd = self.gen_pwd()
        new_user_id = uu.create_key(username, pwd)
        self.logger.info(f"Create user: {username} pwd: {pwd} user_id: {new_user_id.hex()}")
        self.user_res = None
        self.publish_device('user/add', 
                uu.create_user(new_user_id, 0xff, username).decode('utf-8'), 
                user_id)
        time.sleep(10)
        self.assertTrue(self.user_res == None)
        self.logger.info("After 10 sec, still no reply, let's think that message was not authentificated. Good")


    def test(self):
        self.add_users()
        time.sleep(10)
        self.add_existed_user()
        time.sleep(10)
        self.add_wrong_namelen_user()
        time.sleep(10)
        self.add_with_null_perm_user()
        time.sleep(10)
        self.add_without_perm_user()

if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(),"out/tests")))
