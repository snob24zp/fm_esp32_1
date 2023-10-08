import board
import time
import net.webapp as webapp
from config import config_t
import net.mqtt as mqtt
import ntptime
from machine import unique_id


def main():
    net = board.network
    cfg = config_t()
    print(f'Current config: {cfg.json()}')

    time.sleep(5)
    while not net.is_connected():
        print('waiting for network...')
        time.sleep(1)

    ntptime.settime()
    # webapp.init().run(port=80)


if __name__ == '__main__':

    main()
