import board
import time
import webapp
from config import config_t

def main():
    net = board.network
    cfg = config_t()
    print(f'Current config: {cfg.json()}')

    time.sleep(5)
    while not net.is_connected():
        print('waiting for network...')
        time.sleep(1)

    webapp.init().run(port=80, debug=True)


if __name__ == '__main__':
    
    main()
