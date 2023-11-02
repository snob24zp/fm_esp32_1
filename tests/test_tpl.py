
import base64
import json
import string
import traceback
import unittest
import sys
import os
import threading
import random
import time
import logging
import struct

import paho.mqtt.client as mqtt
from collections.abc import Callable


path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(path)
sys.path.append(f'{path}{os.path.sep}src')
sys.path.append(f'{path}{os.path.sep}src{os.path.sep}uclient')

from uclient.hub import HUB
from uclient.fwupd import fwupd_device
import uclient.aes as aes
import user_utils as uu
from config import config_t


class test_tpl(unittest.TestCase):
    MEM_DIR = 'data'

    def setUp(self, dtype=fwupd_device, server=None, token=None, serial=None, user=None, pwd=None, skip_add_user = True, dargs = {}):
        super().setUp()
        self.cfg = config_t()
        if token is not None:
            self.cfg.token = token

        if serial is not None:
            self.cfg.serial = serial

        if server is not None:
            self.cfg.broker = server

        if user is not None:
            self.cfg.user = user

        if pwd is not None:
            self.cfg.pwd = pwd
        
        for _file in os.listdir(f'./{test_tpl.MEM_DIR}'):
            os.unlink(f'./{test_tpl.MEM_DIR}/{_file}')
        
        self.cfg.user_key = uu.create_key(self.cfg.user, self.cfg.pwd)

        self.logger = logging.getLogger('TEST')
        self.__ch = logging.StreamHandler()
        self.__ch.setLevel(logging.INFO)
        self.__formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.__ch.setFormatter(self.__formatter)
        self.logger.addHandler(self.__ch)
        self.logger.setLevel(logging.INFO)
        if 'device_id' in dargs:
             self.cfg.device_id = dargs['device_id']
             del dargs['device_id']
        else:
            self.cfg.device_id = base64.b64decode(self.cfg.device_id)
             
        self._device = dtype(serial = self.cfg.serial, device_id=self.cfg.device_id, **dargs)

        self._uclient = HUB(f'{self.cfg.broker["host"]}:{self.cfg.broker["port"]}', self.cfg.token, [self._device])
        self._uclient.connect()

        self.__hub_thread = threading.Thread(target=self._ucl_step_thread, name="hub-thread", daemon=True)
        self.__hub_thread.start()

        self.wait_condition(lambda: self._uclient.state == HUB.REG_DONE, 60)
        self.mqtt_enable(skip_add_user = skip_add_user)

    def _ucl_step_thread(self):
        while True:
            try:
                if self._uclient is not None:
                    self._uclient.step()
            except Exception as ex:
                 ex_type, ex, tb = sys.exc_info()
                 traceback.print_tb(tb)
                 break

    @staticmethod
    def int2float(b):
        '''
        Преобразовывает число int в float iee754
        '''
        try:
            s = struct.pack('>L', b)
            return struct.unpack('>f', s)[0]
        except Exception:
            return 0

    @staticmethod
    def float2int(b):
        '''
        Преобразовывает число float iee754 в int
        '''
        try:
            s = struct.pack('>f', b)
            return struct.unpack('>L', s)[0]
        except Exception:
            return 0

    def mqtt_enable(self,  skip_add_user=True):
        self.client = mqtt.Client(f"{self.cfg.token}-tester-{'%04x' % random.randrange(16**4)}")
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.on_disconnect = self.__on_disconnect
        self.client.on_log = self.__on_log

        self.is_connected = False
        self.__running = True
        self.__client_thread = threading.Thread(target=self.__main_loop, name="mqtt-thread", daemon=True)
        self.__client_thread.start()

        self.__dev_cbks = {}
        self.__hub_cbks = {}
        self.__direct_cbks = {}
        self.wait_condition(lambda: self.is_connected,20)
        if not skip_add_user:
            self.add_user(self.cfg.user, self.cfg.pwd, key = self.cfg.device_id)
        time.sleep(1)

    def add_user(self, username, pwd, pm=255, acls = [-1], key = None):
        user_res = None

        def on_user_add(topic, value):
            nonlocal user_res
            user_res = value
            
        if key is None:
            key = self.cfg.user_key

        self.subscribe_device('user/add', on_user_add)
        user_id = uu.create_key(username, pwd)
        self.logger.info(f"Create user: {username} pwd: {pwd} user_id: {user_id.hex()}")
        cu = uu.create_user(user_id, pm, username, acls)
        cu_b64 = base64.b64encode(aes.encrypt(cu, key)).decode()

        user_res = None
        self.publish_device('user/add', cu_b64, key)
        self.wait_condition(lambda: user_res is not None, 30)

        self.assertTrue(uu.check(self.cfg.device_id, user_res) is not None)
        user_res = aes.decrypt(base64.b64decode(user_res.split('.')[0]),self.cfg.device_id)
        self.assertTrue(user_res == b'"OK"')

        self.logger.info(f"User created: {user_res.decode()}", )


    def __on_connect(self, client, userdata, flags, rc):
        self.logger.info(f"Connected with result code: {rc}")
        self.client.subscribe(f"/{self.cfg.token}/#")
        self.client.subscribe(f"<{self.cfg.token}/#")
        self.is_connected = True

    def __on_disconnect(self, client, userdata, rc):
        self.client.unsubscribe(f"/{self.cfg.token}/#")
        self.client.unsubscribe(f"<{self.cfg.token}/#")
        self.logger.warning("Disconecting from broker")
        self.is_connected = False

    def __on_log(self, client, userdata, level, buff):
        self.logger.debug("Paho msg: { level: %s, msg: %s }", level, buff)

    def __on_message(self, client, userdata, msg):
        topic = str(msg.topic)
        value = msg.payload.decode("utf-8")

        if topic in self.__direct_cbks and callable(self.__direct_cbks[topic]):
            self.__direct_cbks[topic](topic, value)
            return

        topic = topic[1:].split('/', 2)
        if len(topic) < 2:
            return

        hub = topic[0]
        cmd = topic[1]

        self.logger.debug(f"Event: {{ hub: {hub}, cmd/dev: {cmd}, value: {value} }}")

        if cmd.isnumeric() and int(cmd) == self.cfg.serial:
            cmd = topic[2]
            if cmd in self.__dev_cbks and callable(self.__dev_cbks[cmd]):
                self.__dev_cbks[cmd](cmd, json.loads(value))
                return

        if cmd in self.__hub_cbks and callable(self.__hub_cbks[cmd]):
            self.__hub_cbks[cmd](cmd, value)
            return

        cmd = '/'.join(topic[1:])
        if cmd in self.__hub_cbks and callable(self.__hub_cbks[cmd]):
            self.__hub_cbks[cmd](cmd, value)

    def __main_loop(self):
        '''
        Основной тред mqtt клиента
        '''
        self.__running = True
        while self.__running:
            try:
                self.client.connect(
                    self.cfg.broker['host'], port=int(self.cfg.broker['port']))
                self.client.loop_forever()
            except Exception as r_e:
                logging.error(
                    "Exception raised on main-loop {exception: %s}" % r_e)

    def tearDown(self) -> None:
        self.__running = False
        self._uclient.shutdown()
        self.client.disconnect()
        self._uclient = None
        return super().tearDown()


    def gen_pwd(self, pwd_len=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=pwd_len))

    def gen_username(self):
        ADJECTIVES = ['Affable', 'Agreeable', 'Amiable', 'Charming', 'Polite',
                  'Likeable', 'Gregarious', 'Considerate', 'Sympathetic', 'Understanding']
        NAMES = ['James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer',
                'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Barbara']
        MAIL_HOSTS = ['gmail.com', 'x.ks.ua', 'dlab.pw', 'hotmail.com',
                    'outlook.com', 'vegaiot.com', 'i.ua', 'tlc.ks.ua']

        return f"{random.choice(ADJECTIVES).lower()}.{random.choice(NAMES).lower()}@{random.choice(MAIL_HOSTS)}"


    def subscribe(self, topic: str, cb):
        '''
        Subscribe to direct broker topic
        :topic: Broker topic
        :cb: Callback
        '''
        if cb is not None and callable(cb):
            self.client.subscribe(topic, qos=1)
            self.__direct_cbks[topic] = cb

    def publish(self, topic: str, value: str):
        '''
        Publish to direct broker topic
        '''
        self.client.publish(topic, value.encode('utf-8'), qos=1)

    def subscribe_device(self, topic: str, cb: Callable):
        """
        Subscribe to device topic
        :topic: Device topic
        :cb: Callback
        """
        if cb is not None and callable(cb):
            self.__dev_cbks[topic] = cb

    def subscribe_device_encrypted(self, topic: str, cb: Callable, key: bytes = None):
        """
        Subscribe to device topic
        :topic: Device topic
        :cb: Callback
        """
        if key is None:
            key = self.cfg.device_id
        
        def __cb__(topic, msg):
            nonlocal self, key, cb
            self.assertTrue(uu.check(self.cfg.device_id, msg) is not None)
            msg = aes.decrypt(base64.b64decode(msg.split('.')[0]),key)
            cb(topic, json.loads(msg.decode()))
            
        self.subscribe_device(topic, __cb__)

    def subscribe_hub(self, topic: str, cb):
        """
        Subscribe to hub topic
        :topic: hub topic
        :cb: Callback
        """
        if cb is not None and callable(cb):
            self.__hub_cbks[topic] = cb

    def publish_device(self, topic: str, value: str, key: bytes = None):
        """
        Publish to device topic
        :topic: hub topic
        :cb: Callback
        """
        self.logger.info(f"[dev] => {{ '{topic}' : '{ value if len(str(value)) < 32 else str(value)[:32] }' }}")

        if key is not None:
            value = f"{value}.{uu.sign(key, value)}"
        self.client.publish(f">{self.cfg.token}/{self.cfg.serial}/{topic}", json.dumps(value))

    def publish_device_encrypted(self, topic: bytes, value: bytes, key: bytes = None):
        if isinstance(value, str):
            value = value.encode()

        if key is None:
            key = self.cfg.user_key

        value = base64.b64encode(aes.encrypt(value, key)).decode()
        self.publish_device(topic, value, key)

    def publish_hub(self, topic: str, value, prefix='>'):
        """
        Publish to hub topic
        :topic: hub topic
        :cb: Callback
        """
        self.logger.info(f"[hub] => {{ '{topic}' : '{ value if len(str(value)) < 32 else str(value)[:32] }' }}")
        self.client.publish(f"{prefix}{self.cfg.token}/{topic}", value)

    def wait_random(self, max, min=0):
        """
        Wait random time
        :param max Maximum time to wait
        :param min Minimum time that can be waited
        """
        rnd_sleep = random.uniform(min, max)
        print("Wait for (random): %f seconds" % rnd_sleep)
        time.sleep(rnd_sleep)

    def wait_condition(self, cond, timeout):
        """
        Wait for condition in callable function
        Example:  self.wait_condition(lambda: self.a == self.b,timeout)
        """
        if callable(cond):
            start_time = time.perf_counter()
            while(not cond()):
                self.assertTrue(time.perf_counter() < (start_time + timeout))
                time.sleep(0.01)
            self.logger.info(f"OP take: {round((time.perf_counter() - start_time) * 1000, 3)} ms")
        #time.sleep(0.1)


if __name__ == "__main__":
    unittest.main()
