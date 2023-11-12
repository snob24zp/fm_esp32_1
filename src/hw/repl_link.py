import sys
import select
from hw.link import link


class repl_link(link):
    def __init__(self, rx_cb = None):
        link.__init__(self, rx_cb)
        self.__spoll = select.poll()
        self.__spoll.register(sys.stdin, select.POLLIN)

    def tx(self, data: bytes):
        '''
        Transmit data to the outside
        '''
        sys.stdout.buffer.write(data)

    def recv(self):
        '''
        Try to receive data from outside
        '''
        stdin_buf = bytearray()
        ret = self.__spoll.poll(1)
        while len(ret) > 0:
            stdin_buf.extend(sys.stdin.buffer.read(ret[0][1]))
            ret = self.__spoll.poll(1)
        if len(stdin_buf) > 0:
            try:
                return stdin_buf
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


