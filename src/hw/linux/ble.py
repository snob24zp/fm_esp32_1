'''Virtual Bluetooth driver'''
from log import log


class BLEUART(log):
    '''Virtual Bluetooth driver'''

    def __init__(self, ble=None, name="AR-UART", rxbuf=128):
        super().__init__(f'BLE-{name}')

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        '''Opens BLE connection'''
        pass

    def irq(self, handler):
        '''Set handler on rx (not used)'''
        pass

    def any(self):
        '''Check is there any data in the buffer'''
        return False

    def read(self, sz=None):
        '''Read data from buffer'''
        return bytes(0)

    def write(self, data):
        '''Write data to buffer'''
        self.info(f'TX: {data}')

    def close(self):
        '''Close the BLE'''
        self.info('BLE Closed')
