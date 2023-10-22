import board
import time
from config import config_t
import net.webapp as webapp

import sys
if sys.version.count('MicroPython') > 0:
    import ntptime
    import _thread 
else:
    import threading


def start_thread(cb, args):
    if sys.version.count('MicroPython') > 0:
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
            
            start_thread(lambda: webapp.init().run(port=80),())

        if hasattr(board, "ble"):
            def on_ble_rx(rx):
                pass
            
            ble = board.ble
            ble.irq(on_ble_rx)
    else:
        start_thread(lambda: webapp.init().run(port=3000),())
        while True:
            time.sleep(1)



if __name__ == '__main__':
    main()
