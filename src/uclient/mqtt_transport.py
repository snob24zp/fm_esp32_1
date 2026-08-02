#!/usr/bin/env python3
"""
MQTT Transport abstraction layer
"""

import gc
import time
from log import log
from net.mqtt import MQTTClient
from uclient.transport import transport
import sys
if sys.version.count('MicroPython') > 0:
    from machine import reset
else:
    def reset():
        print('Reseting device')




class mqtt_transport(transport, log):
    '''MQTT Transport layer, which uses default micropython mqtt client'''
    # Fixed client ID for AWS IoT Core (must match thing name in AWS)
    CLIENT_ID = "esp32-c3-mpy-test"

    def __init__(self, name: str) -> None:
        transport.__init__(self, name)
        log.__init__(self, 'MQTT')

        # Enable automatic GC when heap is low (MicroPython)
        try:
            gc.threshold(10000)
        except Exception:
            pass

        self._lw = None
        self.client = None
        self.host = 'a3bb1kruav9c9p-ats.iot.eu-central-1.amazonaws.com'
        self.port = 8883
        self._ssl_params = None
        self.__on_connect_cb = None
        self.__on_disconnect_cb = None
        self.__subscribers = {}

    @log.dbg_wr
    def connect(self, host: str, port: int = 1883, user = None, password = None, use_ssl = False, ssl_params = None) -> None:
        '''Connect to the broker
        :param host: Broker host
        :param port: Broker Port, by default 1883
        :param user: MQTT Username
        :param password: MQTT Password
        :param use_ssl: Use SSL/TLS
        :param ssl_params: SSL parameters (key, cert, cadata, server_hostname)
        '''
        self.host = host
        self.port = port
        self._ssl_params = ssl_params

        # Free memory before creating new TLS client
        gc.collect()

        self.client = MQTTClient(mqtt_transport.CLIENT_ID, host, port,
                                    keepalive=60, user=user, password=password,
                                    ssl=use_ssl, ssl_params=ssl_params)
        if self._lw is not None:
            self.client.set_last_will(self._lw[0], self._lw[1], qos=1)

        self.client.set_callback(self.__on_message)
        gc.collect()
        self.info(f'Free mem before MQTT connect: {gc.mem_free()} bytes')
        self.client.connect()
        time.sleep(1)
        for t in self.__subscribers.keys():
            self.info(f'Subscribe to {t}')
            self.client.subscribe(t)

        if callable(self.__on_connect_cb):
            self.__on_connect_cb()


    @log.dbg_wr
    def publish(self, topic: str, value: bytes, qos: int = 0) -> None:
        '''Publish message'''
        if self.client is not None:
            self.client.publish(topic, msg=str(value), qos=qos)

    @log.dbg_wr
    def subscribe(self, topic: str, callback: object) -> None:
        '''Subscribe to topic'''
        if callback is not None and callable(callback):
            self.__subscribers[topic] = callback
            if self.client is not None:
                self.client.subscribe(topic)

    @log.dbg_wr
    def unsubscribe(self, topic: str) -> None:
        '''Unsubscribe from topic'''
        if topic in self.__subscribers.keys():
            #if self.client is not None:
            #    self.client.unsubscribe(topic)
            del self.__subscribers[topic]

    @log.dbg_wr
    def disconnect(self) -> None:
        '''Disconnect from server'''
        if self.client is not None:
            self.__subscribers = {}
            #    self.client.unsubscribe(t)
            self.client.disconnect()
            self.client = None

    @log.dbg_wr
    def on_connect(self, callback: object) -> None:
        '''Set callback which calls on connect'''
        self.__on_connect_cb = callback

    @log.dbg_wr
    def on_disconnect(self, callback: object) -> None:
        '''Set callback which calls on disconnect'''
        self.__on_disconnect_cb = callback

    @log.dbg_wr
    def set_lastwill(self, topic: str, data: str):
        '''Set last-will message'''
        self._lw = [topic, data]

    def __on_connect(self):
        if callable(self.__on_connect_cb):
            self.__on_connect_cb()

    def __on_disconnect(self):
        if callable(self.__on_disconnect_cb):
            self.__on_disconnect_cb()

    def __on_message(self, topic: bytes, payload: bytes):
        topic = topic.decode()

        if topic in self.__subscribers.keys():
            self.__subscribers[topic](topic, payload)
        else:
            for s in self.__subscribers.keys():
                k = str(s)[:-1]
                if str(s).endswith('#') and str(topic).startswith(k):
                    self.__subscribers[s](topic, payload)

    def __reconnect(self):
        _int_reconnect = 1
        self.__on_disconnect()
        while True:
            try:
                if self.client is None:
                    return

                self.warn(f'Reconnecting in {_int_reconnect}s')
                time.sleep(_int_reconnect)
                # Close old client/socket to free memory before TLS handshake
                if self.client is not None:
                    try:
                        self.client.disconnect()
                    except Exception:
                        pass
                    self.client = None
                gc.collect()
                self.connect(self.host, self.port, use_ssl=self._ssl_params is not None,
                             ssl_params=self._ssl_params)
                self.__on_connect()
                return
            except OSError as e:
                self.err(f'OS-Error: {e}')
                _int_reconnect *= 2
                if _int_reconnect > 256:
                    reset()

    def step(self):
        '''Make a step (ie maintenance method)'''
        try:
            if self.client is not None:
                self.client.check_msg()
        except OSError as ex:
            if ex.errno != 11: # blocking issue on cpython
                self.__reconnect()


def test():
    mq = mqtt_transport('tst-mq-client')
    mq.connect('a3bb1kruav9c9p-ats.iot.eu-central-1.amazonaws.com', port=8883,
               use_ssl=True, ssl_params={
                   "key": open("certs/ecc-key.der", "rb").read(),
                   "cert": open("certs/ecc-crt.der", "rb").read(),
                   "cadata": open("certs/root_ca.der", "rb").read(),
                   "server_hostname": "a3bb1kruav9c9p-ats.iot.eu-central-1.amazonaws.com",
               })
    mq.subscribe('/00:11:22:33:44:55/#', lambda topic, val: print(f'A: {topic} -> {val}'))
    mq.subscribe('/topic_b/#', lambda topic, val: print(f'B: {topic} -> {val}'))

    _pub_time = time.ticks_ms()
    while True:
        if time.ticks_ms() > (_pub_time + 10000):
            mq.publish('/reg', b'00:11:22:33:44:55')
            _pub_time = time.ticks_ms()

        mq.step()


if __name__ == '__main__':
    test()
