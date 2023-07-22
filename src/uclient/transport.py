#!/usr/bin/env python3


class transport():
    '''
    Транспортный уровень для uclient
    '''

    def __init__(self, name: str):
        self.name = name

    def connect(self, host: str, port: int) -> None:
        '''
        Подключение к серверу
        '''
        pass

    def subscribe(self, topic: str, callback : object) -> None:
        '''
        Подпись на топик
        '''
        pass

    def unsubscribe(self, topic: str):
        '''
        Отпись от топика
        '''
        pass

    def publish(self, topic: str, value: bytes, qos: int = 0) -> None:
        '''
        Публикация топика
        '''
        pass

    def disconnect(self) -> None:
        '''
        Отключение от сервера
        '''
        pass

    def on_connect(self, callback: object):
        '''
        По подключению к брокеру
        '''
        pass

    def on_disconnect(self, callback: object):
        '''
        По отключению от брокера
        '''
        pass
