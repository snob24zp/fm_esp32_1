import board
import time
from config import config_t
import net.webapp as webapp

#from net.mqtt import test

import sys
import json
from uclient.device import device_base
if sys.version.count('MicroPython') > 0:
    import ntptime
    import machine
else:
    import code

from log import log
from uclient.fwupd import fwupd_device
from uclient.hub import HUB
from threadmpy import start_thread

device = None
hub = None

class uart_device(fwupd_device):
    def __init__(self, serial, dtype=device_base.DEVICE_TYPE, regs={}, status=0):
        super().__init__(serial, dtype, regs, status, bytes.fromhex(config_t().device_id))
        board.uplink.on_rx(self.on_rx_uart)
        self.ble = None
        self.qble = []
        self.quart = []
        self.qmqtt = []
        self.led_lock = False

    def set_ble(self, ble):
        if ble is None:
            return

        self.ble = ble
        self.ble.irq(lambda d: self.qble.append(d))
        self.ble.open()

    def on_rx_uart(self, _, value: bytes):
        board.led[0] = (0x00, 0xff, 0x00)
        board.led.write()
        self.quart.append(value)

    def on_change_reg(self, topic: str, msg: object):
        if self.isnumeric(topic) and int(topic) == 3:
            if not self.led_lock:
                board.led[0] = (0xff, 0x00, 0x00)
                board.led.write()
            if isinstance(msg, str):
                self.qmqtt.append(msg)
            else:
                self.qmqtt.append(json.dumps(msg).encode())

        if self.isnumeric(topic) and int(topic) == 4:
            if sys.version.count('MicroPython') > 0 and isinstance(msg, int):
                board.led[0] = ((msg >> 16) & 0xff, (msg >> 8) & 0xff, msg & 0xff)
                board.led.write()
                self.led_lock = msg != 0

        if self.isnumeric(topic) and int(topic) == 5:
            if sys.version.count('MicroPython') > 0 and isinstance(msg, dict):
                self.info(f"try to send sms: {msg}")
                try:
                    board.modem.sms(msg['to'], msg['msg'])
                except Exception as ex:
                    print(ex)

        if self.isnumeric(topic) and int(topic) == 6:
            if sys.version.count('MicroPython') > 0 and isinstance(msg, int):
                cfg = config_t()
                cfg.force_wlan = msg > 0
                cfg.save()
                machine.reset()

        return super().on_change_reg(topic, msg)

    def step(self):
        board.uplink()
        if len(self.qble) > 0:
            for _q in self.qble:
                board.uplink.tx(_q)
                self.set_reg(3, _q.decode())
            del self.qble
            self.qble = []

        if len(self.quart) > 0:
            for _q in self.quart:
                if self.ble is not None:
                    self.ble.write(_q)
                self.set_reg(3, _q.decode())
                if not self.led_lock:
                    board.led[0] = (0x00, 0x00, 0x00)
                    board.led.write()
            del self.quart
            self.quart = []

        if len(self.qmqtt) > 0:
            for _q in self.qmqtt:
                if self.ble is not None:
                    self.ble.write(_q)
                board.uplink.tx(_q)
                if not self.led_lock:
                    board.led[0] = (0x00, 0x00, 0x00)
                    board.led.write()
            del self.qmqtt
            self.qmqtt = []

        return super().step()

def led_cycle(color = (1,1,1)):
    for i in range(0, 250, 10):
        board.led[0] = (int(i * color[0]),int(i * color[1]), int(i * color[2]))
        board.led.write()
        time.sleep_ms(10)
    for i in range(250, 0, -10):
        board.led[0] = (int(i * color[0]), int(i * color[1]) , int(i * color[2]))
        board.led.write()
        time.sleep_ms(10)
    board.led[0] = (0,0,0)
    board.led.write()

def modem_est():
    cfg = config_t()
    if hasattr(board, "modem") and not cfg.force_wlan:
        net = board.modem
        if net.init():
            time.sleep(5)
            _start = time.time()
            while not net.is_connected() and time.time() < (_start + 30):
                print('waiting for network (LTE)...')
                led_cycle()
            try:
                ntptime.settime()
            except:
                print('Could not get update from NTP server')
            return net.is_connected()
    return False

def wlan_est(modem_init):
    cfg = config_t()
    if hasattr(board, "network") and not modem_init:
        net = board.network
        net.init()
        time.sleep(5)
        _start = time.time()
        while not net.is_connected() and time.time() < (_start + 30):
            print('waiting for network (WIFI)...')
            
            #led_cycle()  #RDD TODO freezed
            
            time.sleep_ms(2000)
            print('waiting for network (WIFI)...1')

        if cfg.wlan_mode == 0:
            print('waiting for network (WIFI)...2')
            try:
                ntptime.settime()
                print('waiting for network (WIFI)...3')
            except:
                print('Could not get update from NTP server')

            print('waiting for network (WIFI)...4')    
            return net.is_connected()
            

    return False

def main():
    global device, hub
    log.set_log_lvl(log.DEBUG)
    cfg = config_t()
    print(f'Current config: {cfg.json()}')
    if sys.version.count('MicroPython') > 0:
        led_cycle()
        if not board.rst_pad.value():
            _tm = 5
            while _tm and not board.rst_pad.value():
                led_cycle((0,0,1))
                time.sleep_ms(500)
                _tm -= 1

            if _tm == 0:
                cfg.reset()

        board.led[0] = (0,0,0x10)
        board.led.write()
        modem_init = False # modem_est()
        wlan_init = wlan_est(modem_init)

        # while cfg.wlan_mode == 0 and not wlan_init and not modem_init:
        #     #led_cycle(1,0,0)
        #     wlan_init = wlan_est(modem_init)
     
        if cfg.wlan_mode == 0 and not wlan_init and not modem_init:
            print('No network connection established. Please check your configuration.')
            time.sleep(1)
            cfg.reset()


        if cfg.wlan_mode == 1 and not wlan_init:
            board.led[0] = (0x10, 0x00, 0x00)
            board.led.write()
            webapp.init().run(port=80, debug=True)

        if wlan_init:
            print('IP config: ', board.network.ifconfig())
            # start_thread(lambda: webapp.init().run(port=80), (), 8192)  # WEBAPP disabled when working via MQTT
            
        # >>> ВСТАВЛЯТЬ СЮДА <<<
        # test of AWS IoT Core MQTT connection and publish
        # import os

        # print('os.stat("certs/cert.der")[6]:', os.stat("certs/cert.der")[6])
        # print('os.stat("certs/key.der")[6]:', os.stat("certs/key.der")[6])


        # # Сеть уже поднялась. Запускаем изолированный тест AWS IoT Core:
        # print("=== ЗАПУСК ОТЛАДКИ AWS MQTT ===")
        # from net.mqtt import test
        # test()
        # return
        # >>> КОНЕЦ ВСТАВКИ <<<    

        if wlan_init or modem_init:
            board.led[0] = (0x10, 0x10 , 0)
            board.led.write()
            device = uart_device(cfg.serial)
            if hasattr(board, "ble") and not wlan_init:
                device.set_ble(board.ble)

            _usr = None if cfg.srv_user == "" else cfg.srv_user
            _pwd = None if cfg.srv_pwd == "" else cfg.srv_pwd
            hub = HUB(cfg.server, cfg.token, [device], _usr, _pwd)
            hub.connect()

            board.led[0] = (0x00, 0x00, 0x00)
            board.led.write()
            while hub.is_connected:
                hub.step()

            machine.reset()
            
        while True:
            pass

    else:
        banner = '''Set register from shell: device.set_reg(num, value)

Connect to the Serial terminal at /tmp/uart
'''
        device = uart_device(cfg.serial)
        _usr = None if cfg.srv_user == "" else cfg.srv_user
        _pwd = None if cfg.srv_pwd == "" else cfg.srv_pwd
        hub = HUB(cfg.server, cfg.token, [device], _usr, _pwd)
        hub.connect()

        def webapp_run():
            webapp.init().run(port=3000)

        def dev_step_thread():
            global hub
            while hub.is_connected:
                hub.step()

        start_thread(webapp_run, (), 8 * 1024)
        start_thread(dev_step_thread, (), 8 * 1024)

        code.interact(banner, local=locals())
        #dev_step_thread()


if __name__ == '__main__':
    main()
