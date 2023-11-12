from link import link

class uart_link(link):
    def __init__(self, uart, rx_cb = None, timeout = 0, threshold = 0):
        link.__init__(self, rx_cb, timeout)
        self.__uart = uart
        self._threshold = threshold

    def tx(self, data: bytes):
        '''
        Transmit data to the outside
        '''
        self.__uart.write(data)
        self.__uart.flush()

    def poll(self):
        ret_sz = self.__uart.any()
        if ret_sz > self._threshold and self.rx_cb is not None:
            _ret = self.__uart.read(ret_sz)
            if _ret is not None:
                self.rx_cb(self, _ret)
