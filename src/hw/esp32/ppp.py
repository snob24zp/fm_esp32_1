
import network
import time
from hw.net_if import net_if


class modem(net_if):
    '''Modem module (in our case A7672)'''

    def __init__(self, uart_link, pwr_pin) -> None:
        '''Modem module, A7672'''
        super().__init__()
        self.log_prefix = 'GSM'
        self.uart_link = uart_link
        self.pwr_pin = pwr_pin
        self.ppp = None
        self.__sms_ready = False
        self.__rxmsg = ''
        self._states = (
            ("AT\r\n", "OK"),
            ("ATE0\r\n", "OK"),
            ("AT+CPIN?\r\n", "OK"),
            ("AT+CFUN=1\r\n", "OK"),
            ("AT+CEREG?\r\n", "OK"),
            ('AT+CGDCONT=1,"IP","\T","",0,0\r\n', "OK"),
            ('ATD*99#\r\n', 'CONNECT'),
        )
        self.uart_link.on_rx(self.__rx)

    def __rx(self, ul, data):
        '''Callback which calls on receive message from UART'''
        self.__rxmsg += data.decode()
        self.dbg(f'< {self.__rxmsg[:-2]}')

    def __cmd(self, data: str):
        '''Sends AT command'''
        self.__rxmsg = ''
        self.dbg(f'> {data[:-2]}')
        self.uart_link.tx(data.encode())

    def __waitfor(self, answ, timeout=10000):
        '''waits for AT command answer'''
        _start = time.ticks_ms()
        while time.ticks_ms() < (_start + timeout) and self.__rxmsg.count(answ) == 0:
            self.uart_link.poll()

        if time.ticks_ms() > (_start + timeout) or self.__rxmsg.count(answ) == 0:
            return False

        self.__rxmsg = ''
        return True

    def is_connected(self):
        '''Is modem currently connected or not'''
        if self.ppp:
            return self.ppp.isconnected()
        return False

    def ifconfig(self, ip=None, mask=None, gw=None, dns=None):
        '''Return current PPP configuration'''
        if self.ppp is not None:
            if ip is None:
                return self.ppp.ifconfig()

    def __tg_pwr_pin(self):
        '''toggle PWR pin'''
        self.pwr_pin(0)
        time.sleep(0.1)
        self.pwr_pin(1)
        time.sleep(1)
        self.pwr_pin(0)

    def __wait_ready(self):
        '''Waits while modem is not ready'''
        if self.__waitfor("*ATREADY: 1", 20000):
            self.info('AT-Ready found')

        if self.__waitfor("PB DONE"):
            self.info('Modem ready')
        time.sleep(1)

    def __activate_ppp(self):
        '''Activating PPP link'''
        self.ppp = network.PPP(self.uart_link.__uart)
        self.ppp.active(True)
        self.ppp.connect()

    def init(self):
        '''Bring up the PPP connection'''
        self.__tg_pwr_pin()
        self.info('RST done')
        self.__wait_ready()

        for state in self._states:
            _start = time.ticks_ms()
            self.__cmd(state[0])
            if not self.__waitfor(state[1]):
                self.warn(f'Command {state[0]} timeout')
                return False

            self.info(f'{state[0][:-2]} <--> OK')

        self.info('Activating PPP connection')
        self.__activate_ppp()
        return True

    def sms(self, to, msg):
        '''Send SMS'''
        if self.is_connected():
            self.info("Can't send sms while PPP session is ongoing")
            return
        
        if not self.__sms_ready:
            self.__tg_pwr_pin()
            self.info('RST done')
            self.__wait_ready()
            self.__sms_ready = True

        self.__cmd("AT+CMGF=1\r\n")
        if not self.__waitfor("OK"):
            self.warn('AT+CMGF=1 failed')
            return
        self.__cmd('AT+CSCS="GSM"\r\n')
        if not self.__waitfor("OK"):
            self.warn('AT+CSCS failed')
            return

        self.__cmd(f'AT+CMGS="{to}"\r\n')
        self.__cmd(f'{msg}\r\n')
        self.__cmd(f'\x1a')
        self.__waitfor("OK")
