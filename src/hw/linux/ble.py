# This example demonstrates a peripheral implementing the Nordic UART Service (NUS).

# This example demonstrates the low-level bluetooth module. For most
# applications, we recommend using the higher-level aioble library which takes
# care of all IRQ handling and connection management. See
# https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble

from log import log


class BLEUART(log):
    def __init__(self, ble=None, name="AR-UART", rxbuf=128):
        super().__init__(f'BLE-{name}')

    def irq(self, handler):
        self._handler = handler

    def any(self):
        return False


    def read(self, sz=None):
        return bytes(0)

    def write(self, data):
        self.info(f'TX: {data}')

    def close(self):
        self.info('BLE Closed')
