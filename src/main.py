import board
import time
import base64
import hashlib
from config import config_t
import net.webapp as webapp

import sys
from uclient.device import device_base
if sys.version.count('MicroPython') > 0:
    import ntptime
    import _thread 
else:
    import threading
    import code

from uclient.evtdev import event_device
from uclient.userdev import user_device
from uclient.hub import HUB


def gen_device_id():
    return hashlib.sha256(b'DUT').digest()


class uart_device(user_device, event_device):
    def __init__(self, serial, dtype=device_base.DEVICE_TYPE, regs={}, status=0):
        super().__init__(gen_device_id(), serial, dtype, regs, status)
        super(user_device, self).__init__(serial = serial, dtype= dtype, regs = regs, status = status)


def start_thread(cb, args):
    if sys.version.count('MicroPython') > 0:
        _thread.stack_size(10*1024)
        _thread.start_new_thread(cb, args)
    else:
        _th = threading.Thread(target=cb, name=f"{cb.__name__}-thread", daemon=True, args=args)
        _th.start()



def main():
    cfg = config_t()
    print(f'Current config: {cfg.json()}')
    if sys.version.count('MicroPython') > 0:
        if hasattr(board, "network"):
            net = board.network

            time.sleep(5)
            while not net.is_connected():
                print('waiting for network...')
                time.sleep(1)
            
            if cfg.wlan_mode == 0:
                try:
                    ntptime.settime()
                except:
                    print('Could not get update from NTP server')
                    
                device = uart_device(cfg.serial)
                hub = HUB(cfg.server, cfg.token, [device])
                hub.connect()
                def dev_step_thread():
                    nonlocal hub
                    while hub.is_connected:
                        hub.step()
                start_thread(lambda: dev_step_thread(),())

            start_thread(lambda: webapp.init().run(port=80),())

        if hasattr(board, "ble"):
            def on_ble_rx(rx):
                pass
            
            ble = board.ble
            ble.irq(on_ble_rx)

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

        start_thread(lambda: webapp.init().run(port=3000),())
        start_thread(lambda: dev_step_thread(),())
        code.interact(banner, local=locals())


if __name__ == '__main__':
    main()
