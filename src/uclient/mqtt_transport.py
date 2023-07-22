#!/usr/bin/env python3

import time
from log import log
from net.mqtt import MQTTClient
from uclient.transport import transport


class mqtt_transport(transport, log):
    def __init__(self, name: str) -> None:
        transport.__init__(self, name)
        log.__init__(self, 'MQTT')

        self.client = None
        self.host = 'x.ks.ua'
        self.port = 1883
        self.__subscribers = {}
    
    @log.dbg_wr
    def connect(self, host: str, port: int = 1883) -> None:
        self.host = host
        self.port = port

        self.client = MQTTClient(self.name, host, port, keepalive=60)
        self.client.set_callback(self.__on_message)
        self.client.connect()
        time.sleep(1)
        for t in self.__subscribers.keys():
            self.info(f'Subscribe to {t}')
            self.client.subscribe(t)
        
        if callable(self.__on_connect_cb):
            self.__on_connect_cb()


    @log.dbg_wr
    def publish(self, topic: str, value: bytes, qos: int = 0) -> None:
        if self.client is not None:
            self.client.publish(topic, msg=str(value), qos=qos)

    @log.dbg_wr
    def subscribe(self, topic: str, callback: object) -> None:
        if callback is not None and callable(callback):
            self.__subscribers[topic] = callback
            if self.client is not None:
                self.client.subscribe(topic)

    @log.dbg_wr
    def unsubscribe(self, topic: str) -> None:
        if topic in self.__subscribers.keys():
            #if self.client is not None:
            #    self.client.unsubscribe(topic)
            del self.__subscribers[topic]

    @log.dbg_wr
    def disconnect(self) -> None:
        if self.client is not None:
            self.__subscribers = {}
            #    self.client.unsubscribe(t)
            self.client.disconnect()
            self.client = None

    @log.dbg_wr
    def on_connect(self, callback: object) -> None:
        self.__on_connect_cb = callback

    @log.dbg_wr
    def on_disconnect(self, callback: object) -> None:
        self.__on_disconnect_cb = callback

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
                self.connect(self.host, self.port)
                self.__on_connect()
                return
            except OSError as e:
                self.err(f'OS-Error: {e}')
                _int_reconnect *= 2

    def step(self):
        try:
            if self.client is not None:
                self.client.check_msg()
        except OSError as ex:
            if ex.errno != 11: # blocking issue on cpython
                self.__reconnect()


def test():
    mq = mqtt_transport('tst-mq-client')
    mq.connect('x.ks.ua')
    mq.subscribe('/00:11:22:33:44:55/#', lambda topic, val: print(f'A: {topic} -> {val}'))
    mq.subscribe('/topic_b/#', lambda topic, val: print(f'B: {topic} -> {val}'))
    
    _pub_time = time.ticks_ms()
    while(True):
        if time.ticks_ms() > (_pub_time + 10000):
            mq.publish('/reg', b'00:11:22:33:44:55')
            _pub_time = time.ticks_ms()

        mq.step()
        

if __name__ == '__main__':
    test()
