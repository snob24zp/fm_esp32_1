from polled import polled

class link(polled):
    def __init__(self, rx_cb = None, timeout = 0):
        polled.__init__(self, interval=timeout)
        self.rx_cb = rx_cb if rx_cb is not None and callable(rx_cb) else None

    def tx(self, data):
        '''
        Transmit data to the outside
        '''
        print(data)

    def on_rx(self, cb):
        '''
        Set receive callback
        '''
        if cb is not None and callable(cb):
            self.rx_cb = cb
