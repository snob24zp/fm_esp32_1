from hw.link import link

class uart_link(link):
    def __init__(self, uart, rx_cb = None, timeout = 0, threshold = 0):
        link.__init__(self, rx_cb, timeout)
        self.__uart = uart
        self._threshold = threshold

    def tx(self, data: bytes):
        '''
        Transmit data to the outside
        '''
        print(f'[DBG] uart_link.tx() enter, len={len(data)}')
        self.__uart.write(data)
        print(f'[DBG] uart_link.tx() write OK')
        self.__uart.flush()
        print(f'[DBG] uart_link.tx() flush OK')

    def poll(self):
        try:
            ret_sz = self.__uart.any()
            # Вычитываем ВСЁ, что накопилось по таймауту/прерыванию
            if ret_sz > self._threshold and self.rx_cb is not None:
                _ret = self.__uart.read(ret_sz)
                if _ret is not None:
                    self.rx_cb(self, _ret)
        except OSError as ex:
            print(f'!!! UART exception !!! {self.__uart} -> {ex}')
