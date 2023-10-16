#!/usr/bin/env python3

try:
    from time import ticks_ms
except ImportError:
    import time
    def ticks_ms():
        return int(time.time() * 1000)

import json

import gc
import base64
import hashlib


from log import log
from version import STATIC_VERSION

from uclient.mqtt_transport import mqtt_transport as mqtt
from uclient.device import device_base


class HUB(log):
    '''
    Класс клиента
    '''
    REG_DEREG = 0          # Клиент не зарегистрирован на сервере
    REG_SEND_SRV_DATA = 1  # Клиент будет отправлять информацию о себе
    REG_DONE = 2           # Регистрация выполнена успешна
    REG_BLOCKED = 5        # Сервер запретил выполнения данного клиента

    VERSION = STATIC_VERSION     # Версия эмулятора

    def __init__(self, server, token, devices):
        '''
        Класс клиента
        '''
        log.__init__(self, f'HUB')

        self.server = server
        self.token = token
        self.devices = []

        for dev in devices:
            self.devices.append(dev)
            dev.set_hub(self)

        self.root_hub_hnd = [
            ["time", self.__time_hnd, '/'],
            ["lifetime", self.__lifetime_hnd, '>'],
            ["error", self.__error_hnd, '>'],
            ["ping", self.__ping_hnd, '>']
        ]

        self._on_chg_state = None
        self._on_disconnect_cb = None
        self._on_reg_upd = None

        self._old_state = None

        self.events_disable = False
        self.client = mqtt(token.replace(':', ''))
        self.client.on_connect(self.__on_connect)
        self.client.on_disconnect(self.__on_disconnect)
        self.time = None
        self.status = 0
        self.state = self.REG_DEREG
        self.is_connected = False
        self.lifetime = 3
        self.pub_tmr = ticks_ms()

    def pub(self, topic, value):
        if self.state == self.REG_DONE:
            self.pub_hub(topic, value)
            self.status += 1
            return True
        return False

    def pub_hub(self, topic, value, prefix='<'):
        '''
        Отправляет данные в указанный топик с префиксом хаба
        '''
        self.info(f"Publish message: {{ topic: {topic}, value: {value} }}")
        self.client.publish(f"{prefix}{self.token}/{topic}", value)

    def subscribe_hub(self, topic, prefix="/"):
        '''
        Подписывается на топик хаба
        '''
        topic = f"{prefix}{self.token}/{topic}"
        self.info(f"(HUB) Subscribe to : {{topic: {topic} }}")
        self.client.subscribe(topic, self.__on_message)

    def __time_hnd(self, value):
        '''
        Обработчик /{hub}/time
        '''
        self.time = int(value)
        if self.state == self.REG_DEREG:
            self.info(f"Registration finish, time: {value}")
            self.state = self.REG_SEND_SRV_DATA
            tm = int(value) // 1000
            for dev in self.devices:
                dev.register(tm)

    def __lifetime_hnd(self, value):
        '''
        Обработчик /{hub}/lifetime
        '''
        self.info("Set new lifetime: {lifetime: %s}", value)
        self.lifetime = int(value)

    def __error_hnd(self, value):
        '''
        Обработчик /{hub}/error
        '''
        self.info("Server error command: {value: %d}", int(value))
        if int(value) == 1:
            self.state = self.REG_DEREG
            if self._on_chg_state is not None and callable(self._on_chg_state):
                self._on_chg_state(self.state)
            self.status = 0
        if int(value) == 2:
            self.state = self.REG_BLOCKED

        if int(value) == 3:
            self.state = self.REG_SEND_SRV_DATA
            self.lifetime = 1

        if int(value) == 4:
            self.events_disable = True

    def __ping_hnd(self, value):
        '''
        Обработчик /{hub}/ping
        '''
        self.info("Ping command")
        self.pub_hub("ping", "ok")

    def __send_reg(self):
        '''
        Отправляет {hub} на регистрацию
        '''
        if self.is_connected:
            self.info(f"Publish reg token: {self.token}")
            self.client.publish("/reg", self.token, qos=1)

    def __on_connect(self):
        '''
        Обработчик по подключению mqtt клиента
        '''
        self.info("Connected")
        self.client.subscribe(">hub", self.__on_message)
        self.client.subscribe(">user/dev", self.__on_message)
        for root_hub_topic in self.root_hub_hnd:
            self.subscribe_hub(root_hub_topic[0], root_hub_topic[2])
        self.is_connected = True
        self.dereg()

    def __on_disconnect(self):
        '''
        Обработчик по отключению mqtt клиента
        '''

        self.warn("Disconecting from broker")
        self.is_connected = False
        self.state = self.REG_DEREG
        self.status = 0
        if self._on_disconnect_cb is not None and callable(self._on_disconnect_cb):
            self._on_disconnect_cb()

    def __hub_topic_hnd(self, topic: str, value: bytes):
        '''
        Обработчик топика >hub
        '''
        if topic == ">hub":
            value = value.decode("utf-8")
            search_dev = int(value)
            for dev in self.devices:
                if dev.serial == search_dev:
                    self.client.publish('<hub', self.token, qos=1)
                    return True
        return False

    def __user_devs_hnd(self, topic: str, payload: bytes):
        '''
        Обработчик топика >user/dev
        '''
        if topic == ">user/dev":
            value = payload.decode("utf-8")
            search_usr = base64.b64decode(value)
            for dev in self.devices:
                for usr in dev.users:
                    _usr_hh = hashlib.sha256(usr.uid).digest()
                    if _usr_hh == search_usr:
                        self.client.publish('>user/dev', f"/{self.token}/{dev.serial}", qos=1)
            return True
        return False

    def __on_message(self, topic: str, payload: bytes):
        '''
        Обработчик входящего сообщения
        '''

        # try:
        value = payload.decode("utf-8")
        self.info(f"Message: {{topic: {topic}, value: {value} }}")

        if self.__hub_topic_hnd(topic, payload):
            return

        if self.__user_devs_hnd(topic, payload):
            return

        if topic.startswith(f'/{self.token}/') or topic.startswith(f'>{self.token}/'):
            topic = topic[len(f'/{self.token}/'):]
            for root_hub_topic in self.root_hub_hnd:
                if topic == root_hub_topic[0]:
                    root_hub_topic[1](value)
                    return

            for dev in self.devices:
                if topic.startswith(f'{dev.serial}/'):
                    dev.hnd_msg(topic[len(f'{dev.serial}/'):], json.loads(value))

        # except Exception as e:
        #     self.err(f"on_msg exception: {e}")

    def step(self):
        '''
        Тред обработки состояний клиента
        '''
        self.client.step()
        for dev in self.devices:
            dev.step()

        if self.pub_tmr + (self.lifetime * 1000) > ticks_ms():
            return

        try:
            self.pub_tmr = ticks_ms()
            self.dbg(f'Step, state: {self.state} (next: {self.pub_tmr + (self.lifetime * 1000) })')

            if self.is_connected:
                if self.state == self.REG_DEREG:
                    self.events_disable = False
                    self.__send_reg()
                    if self._on_chg_state is not None and callable(self._on_chg_state):
                        self._on_chg_state(self.state)

                elif self.state == self.REG_SEND_SRV_DATA:
                    # subscribe to all registers in device and publish info, and device type
                    if self._on_chg_state is not None and callable(self._on_chg_state):
                        self._on_chg_state(self.state)

                    self.pub_hub("info", json.dumps(
                        {
                            "mac": self.token,
                            "version": self.VERSION,
                            "type": "mpy",
                            "prot": 2,
                            "devices": list(map(lambda d: d.info_req(), self.devices)),
                        }), '/')
                    self.lifetime = 60
                    self.state = self.REG_DONE

                elif self.state == self.REG_DONE:
                    self.pub_hub("status", self.status, '/')
                    for dev in self.devices:
                        dev.publish_status()

                    if self._on_reg_upd is not None and callable(self._on_reg_upd):
                        self._on_reg_upd(self)

                elif self.state == self.REG_BLOCKED:
                    self.shutdown()
                    return
                else:
                    self.state = self.REG_DEREG
        except OSError as ex:
            self.dereg()
        except Exception as ex:
            self.err(ex)
            
        finally:
            gc.collect()

    def set_version(self, version: str) -> None:
        self.VERSION = version

    def set_on_disconnect(self, callback):
        if callback is not None and callable(callback):
            self._on_disconnect_cb = callback

    def set_on_reg_upd(self, callback):
        if callback is not None and callable(callback):
            self._on_reg_upd = callback

    def set_on_change_state(self, callback):
        '''
        Устанавливает callback, который будет вызван при изменении состояния сервера
        '''
        if callable(callback):
            self._on_chg_state = callback

    def add_device(self, device):
        '''
        Добавляет новый девайс
        '''
        if device.serial in list(map(lambda d: d.serial, self.devices)):
            self.warn(f'device {device.serial} already added')
            return

        self.devices.append(device)
        device.set_hub(self)
        self.dereg()
        if self._on_chg_state is not None and callable(self._on_chg_state):
            self._on_chg_state(self.state)

    def remove_device(self, serial):
        '''
        Удаляет девайс
        '''
        for dev in self.devices:
            if dev.serial == serial:
                self.devices.remove(dev)
                self.dereg()
                if self._on_chg_state is not None and callable(self._on_chg_state):
                    self._on_chg_state(self.state)

                break

    def dereg(self):
        '''
        Де-регистрирует устройство
        '''
        self.state = self.REG_DEREG
        self.status = 0
        self.lifetime = 1

    def lqi(self, val: int):
        '''
        Публикация значения LQI
        '''
        self.pub_hub('lqi', str(val))

    def shutdown(self):
        """
        Завершает работу
        """
        self.client.disconnect()

    def connect(self):
        """
        Подключается к брокеру
        """
        h = self.server.split(':')
        if len(h) == 1:
            self.client.connect(h[0])
        elif len(h) == 2:
            self.client.connect(h[0], int(h[1]))



def test():
    try:
        from machine import unique_id
    except ImportError:
        import random
        
        def unique_id():
            return random.randbytes(6)

    dev = device_base(12345)
    token = unique_id().hex(":")

    # sha256("ap0\0y78bug57\0")
    cl = HUB("x.ks.ua:1883", token, [dev])
    cl.connect()

    while True:
        cl.step()


if __name__ == '__main__':
    test()
