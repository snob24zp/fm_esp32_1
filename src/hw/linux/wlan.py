'''Virtual WIFI driver'''
from hw.net_if import net_if

class WLAN(net_if):
    '''Virtual WIFI interface'''
    def __init__(self) -> None:
        super().__init__()

    @property
    def mode(self):
        '''Mode'''
        return 0

    def is_connected(self):
        '''Always connected'''
        return True

    def scan(self):
        '''Always send only one '''
        return [(b'simu-wlan-point', b'J\x8fZ\x18s\x13', 1, -62, 4, False)]

    def ifconfig(self, ip=None, mask=None, gw=None, dns=None):
        '''Gets cuurent config of interface'''
        if ip is None:
            return ('192.168.4.1', '255.255.255.0', '192.168.4.1', '192.168.4.1')
        return None
