"""
Antenna rotation control daemon
"""
import socket

class rotctld:
    def __init__(self, host='0.0.0.0', port = 4533):
        self.host = host
        self.port = port
        self._socket = None

    def run(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ai = socket.getaddrinfo(self.host, self.port)

        self._socket.bind(ai[0][-1])
        self._socket.listen(5)


        conn, addr = self._socket.accept()


        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        print('Content = %s' % str(request))
        response = 'Hello'
        conn.send(response)
        conn.close()

