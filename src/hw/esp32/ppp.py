
import network
import time
from log import log


class modem(log):

    def __init__(self, uart_link, pwr_pin) -> None:
        super().__init__('PPP')
        self.uart_link = uart_link
        self.pwr_pin = pwr_pin
        self.ppp = None
        self.__rxmsg = ''
        self._states = (
            ("AT\r\n", "OK"),
            ("ATE0\r\n", "OK"),
            ("AT+CPIN?\r\n", "OK"),
            ("AT+CFUN=1\r\n", "OK"),
            ("AT+CEREG?\r\n", "OK"),
            ('AT+CGDCONT=1,"IP","\T","",0,0\r\n', "OK"),
            ('ATD*99#\r\n', 'OK'),
        )
        self.uart_link.on_rx(self.__rx)

    def __rx(self, ul, data):
        self.__rxmsg += data.decode()
        self.info(f'< {self.__rxmsg[:-2]}')

    def __cmd(self, data: str):
        self.__rxmsg = ''
        self.info(f'> {data[:-2]}')
        self.uart_link.tx(data.encode())

    def __waitfor(self, answ, timeout = 5000):
        _start = time.ticks_ms()
        while time.ticks_ms() < (_start + timeout) and self.__rxmsg.count(answ) == 0:
            self.uart_link.poll()
        
        if time.ticks_ms() > (_start + timeout):
            return False
        
        self.__rxmsg = ''
        return True

    def is_connected(self):
        if self.ppp:
            return self.ppp.isconnected()
        return False

    def init(self):
        self.pwr_pin(0)
        time.sleep(0.1)
        self.pwr_pin(1)
        time.sleep(1)
        self.pwr_pin(0)
        self.info('RST done')
        if self.__waitfor("*ATREADY: 1", 20000):
            self.info('AT-Ready found')

        if self.__waitfor("PB DONE", 10000):
            self.info('Modem ready')

        time.sleep(1)
        for state in self._states:
            _start = time.ticks_ms()
            self.__cmd(state[0])
            if not self.__waitfor(state[1]):
                self.warn(f'Command {state[0]} timeout')
                return False

            self.info(f'{state[0][:-2]} <--> OK')

        self.info('Activating PPP connection')
        self.ppp = network.PPP(self.uart_link.__uart)
        self.ppp.active(True)
        self.ppp.connect()

        return True
