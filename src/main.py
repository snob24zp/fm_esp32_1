import board
import time
from config import config_t
import net.webapp as webapp

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

class uart_device(fwupd_device):
    def __init__(self, serial, dtype=device_base.DEVICE_TYPE, regs={}, status=0):
        super().__init__(serial, dtype, regs, status, bytes.fromhex(config_t().device_id))
        board.uplink.on_rx(self.on_rx_uart)
        self.ble = None
        self.qble = []
        self.quart = []
        self.qmqtt = []

    def set_ble(self, ble):
        if ble is None:
            return

        self.ble = ble
        self.ble.irq(lambda d: self.qble.append(d))
        self.ble.open()

    def on_rx_uart(self, _, value: bytes):
        self.quart.append(value)

    def on_change_reg(self, topic: str, msg: object):
        if self.isnumeric(topic) and int(topic) == 3:
            self.qmqtt.append(json.dumps(msg).encode()[1:-1])
        if self.isnumeric(topic) and int(topic) == 4:
            if sys.version.count('MicroPython') > 0 and isinstance(msg, int):
                board.led[0] = ((msg >> 16) & 0xff, (msg >> 8) & 0xff, msg & 0xff)
                board.led.write()
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
            del self.quart
            self.quart = []

        if len(self.qmqtt) > 0:
            for _q in self.qmqtt:
                if self.ble is not None:
                    self.ble.write(_q)
                board.uplink.tx(_q)
            del self.qmqtt
            self.qmqtt = []

        return super().step()


def main():
    global device
    log.set_log_lvl(log.INFO)
    cfg = config_t()
    print(f'Current config: {cfg.json()}')
    if sys.version.count('MicroPython') > 0:
        modem_init = False
        wlan_init = False
        if hasattr(board, "modem") and not cfg.force_wlan:
            net = board.modem
            if net.init():
                time.sleep(5)
                _start = time.time()
                while not net.is_connected() and _start < (time.time() + 30):
                    print('waiting for network...')
                    time.sleep(1)
                try:
                    ntptime.settime()
                except:
                    print('Could not get update from NTP server')
                modem_init = net.is_connected()

        if hasattr(board, "network") and not modem_init:
            net = board.network
            net.init()
            time.sleep(5)
            _start = time.time()
            while not net.is_connected() and _start < (time.time() + 30):
                print('waiting for network...')
                time.sleep(1)

            if cfg.wlan_mode == 0:
                try:
                    ntptime.settime()
                except:
                    print('Could not get update from NTP server')
            wlan_init = net.is_connected()

        if wlan_init:
            start_thread(lambda: webapp.init().run(port=80), (), 8192)

        if wlan_init or modem_init:
            device = uart_device(cfg.serial)
            if hasattr(board, "ble") and not wlan_init:
                device.set_ble(board.ble)

            _usr = None if cfg.srv_user == "" else cfg.srv_user
            _pwd = None if cfg.srv_pwd == "" else cfg.srv_pwd
            hub = HUB(cfg.server, cfg.token, [device], _usr, _pwd)
            hub.connect()

            def dev_step_thread():
                nonlocal hub
                while hub.is_connected:
                    hub.step()
            dev_step_thread()

    else:
        banner = '''Set register from shell: device.set_reg(num, value)

Connect to the Serial terminal at /tmp/uart
'''
        device = uart_device(cfg.serial)
        _usr = None if cfg.srv_user == "" else cfg.srv_user
        _pwd = None if cfg.srv_pwd == "" else cfg.srv_pwd
        hub = HUB(cfg.server, cfg.token, [device], _usr, _pwd)
        hub.connect()

        def dev_step_thread():
            nonlocal hub
            while hub.is_connected:
                hub.step()

        start_thread(lambda: webapp.init().run(port=3000), (), 128 * 1024)
        start_thread(lambda: dev_step_thread(), (), 128 * 1024)
        code.interact(banner, local=locals())


if __name__ == '__main__':
    main()
