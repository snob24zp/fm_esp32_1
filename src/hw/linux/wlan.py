from config import config_t

class WLAN:
    def __init__(self) -> None:
        self._cfg = config_t()
        self._pre_time = 0
        self._scan = None
        self._wlan = None
        self.scan()
        if self._wlan is None:
            self.init()

    def init(self):
        pass

    @property
    def mode(self):
        return self._cfg.wlan_mode

    def is_connected(self):
        return True

    def scan(self):
        return [(b'simu-wlan-point', b'J\x8fZ\x18s\x13', 1, -62, 4, False)]
    
    def ifconfig(self, ip = None, mask = None, gw = None, dns = None):
        if ip is None:
            return ('192.168.4.1', '255.255.255.0', '192.168.4.1', '192.168.4.1')
        
        if ip is str and ip == "dhcp":
            # self._wlan.ifconfig('dhcp')
            return
        
        if ip is str and mask is str and gw is str and dns is str:
            #set ip
            # self._wlan.ifconfig(ip, mask, gw, dns)
            pass
