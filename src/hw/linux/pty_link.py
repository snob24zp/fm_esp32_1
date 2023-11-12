import select
import os
from hw.link import link


class pty_link(link):
    UART_LNK = '/tmp/uart'

    def __init__(self, pty = UART_LNK, rx_cb = None):
        '''
        PTY (TTY) Link
        '''
        link.__init__(self, rx_cb)
        self.cl_name = pty
        self.__ms, self.__sl = os.openpty()
        self.__ttyname = os.ttyname(self.__sl)
        os.system(f"rm {self.cl_name}")
        os.system(f"ln -s {self.__ttyname} {self.cl_name}")
        self.__spoll = select.poll()
        self.__spoll.register(self.__ms, select.POLLIN)


    def __enter__(self):
        pass


    def tx(self, data: bytes):
        '''
        Transmit data to the outside
        '''
        os.write(self.__ms, data)


    def recv(self):
        '''
        Try to receive data from outside
        '''
        buf = bytearray()
        ret = self.__spoll.poll(1)
        while len(ret) > 0:
            buf.extend(os.read(ret[0][0], 1))
            ret = self.__spoll.poll(10)
        if len(buf) > 0:
            try:
                return buf
            except:
                pass
        return None


    def poll(self):
        '''
        Poll method @see polled.py
        '''
        _ret = self.recv()
        if _ret is not None and self.rx_cb is not None:
            self.rx_cb(self, _ret)


    def __exit__(self):
        '''
        Close sockets
        '''
        os.close(self.__ms)
        os.close(self.__sl)


    def __del__(self):
        '''
        Close sockets
        '''
        os.close(self.__ms)
        os.close(self.__sl)
        super().__del__()