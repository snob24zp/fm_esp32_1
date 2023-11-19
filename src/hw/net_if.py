
from log import log

class net_if(log):
    '''Network interface abstract class'''
    def __init__(self) -> None:
        '''Network inteface abstract class'''
        super().__init__('WAN')

    def init(self):
        '''Initialize connection '''
        pass

    def is_connected(self):
        '''Is connection alive or not'''
        return False

    def scan(self):
        '''Scan for networks (WIFI)'''
        return ()

    def ifconfig(self, ip=None, mask=None, gw=None, dns=None):
        '''Set or get current configuration'''
        if ip is None:
            return ('0.0.0.0', '255.255.255.255', '0.0.0.0', '0.0.0.0')

        if ip is str and ip == "dhcp":
            return

        if ip is str and mask is str and gw is str and dns is str:
            pass
