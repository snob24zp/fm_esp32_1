import board
import time
import hashlib
from config import config_t
import net.webapp as webapp

import sys
import json
from uclient.device import device_base
if sys.version.count('MicroPython') > 0:
    import ntptime
else:
    import code

from uclient.evtdev import event_device
from uclient.userdev import user_device
from uclient.fwupd import fwupd_device
from uclient.hub import HUB
from fwupd import fwupd
from threadmpy import start_thread

def gen_device_id():
    return hashlib.sha256(b'DUT').digest()

device = None

class uart_device(fwupd_device):
    def __init__(self, serial, dtype=device_base.DEVICE_TYPE, regs={}, status=0):
        super().__init__(serial, dtype, regs, status, bytes.fromhex(config_t().device_id))
        board.uplink.on_rx(self.on_rx_uart)

    def on_rx_uart(self, _, value: bytes):
        self.set_reg(3, value.decode())
    
    def on_change_reg(self, topic: str, msg: object):
        if self.isnumeric(topic) and int(topic) == 3:
            board.uplink.tx(json.dumps(msg).encode())
        if self.isnumeric(topic) and int(topic) == 4:
            if sys.version.count('MicroPython') > 0 and isinstance(msg, int):
                board.led[0] = ((msg >> 16) & 0xff, (msg >> 8) & 0xff, msg & 0xff)
                board.led.write()

        return super().on_change_reg(topic, msg)

    def step(self):
        board.uplink()
        return super().step()


def main():
    global device
    cfg = config_t()
    print(f'Current config: {cfg.json()}')
    if sys.version.count('MicroPython') > 0:
        modem_init = False
        wlan_init = False
        if hasattr(board, "modem"):
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
            
        if  hasattr(board, "network") and not modem_init:
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

        if hasattr(board, "ble") and not wlan_init:
            def on_ble_rx(rx):
                pass
            
            ble = board.ble
            ble.irq(on_ble_rx)

        if wlan_init:
            start_thread(lambda: webapp.init().run(port=80),(),8192)

        if wlan_init or modem_init:
            device = uart_device(cfg.serial)
            hub = HUB(cfg.server, cfg.token, [device])
            hub.connect()
            def dev_step_thread():
                nonlocal hub
                while hub.is_connected:
                    hub.step()
            start_thread(lambda: dev_step_thread(),(), 16384)


    else:
        banner = '''Set register from shell: device.set_reg(num, value)
'''
        device = uart_device(cfg.serial)
        hub = HUB(cfg.server, cfg.token, [device])
        hub.connect()
        def dev_step_thread():
            nonlocal hub
            while hub.is_connected:
                hub.step()

        start_thread(lambda: webapp.init().run(port=3000),(), 128 * 1024)
        start_thread(lambda: dev_step_thread(),(), 128 * 1024)
        code.interact(banner, local=locals())


if __name__ == '__main__':
    main()
