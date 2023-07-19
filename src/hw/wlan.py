import network
from config import config_t
import utime
from machine import reset


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
        self._wlan = network.WLAN(self._cfg.wlan_mode)
        self._wlan.active(True)
        if self._cfg.wlan_mode == network.AP_IF:
            self._wlan.config(ssid=self._cfg.ap_ssid,password=self._cfg.ap_pwd)
            print(f'Set up AP: [SSID: {self._cfg.ap_ssid} Password: {self._cfg.ap_pwd}]')
        elif self._cfg.wlan_mode == network.STA_IF:
            utime.sleep_ms(1000)
            print(f'Connecting: [SSID: {self._cfg.sta_ssid} Password: {self._cfg.sta_pwd}]')
            self._wlan.connect(self._cfg.sta_ssid,self._cfg.sta_pwd)
            print(f'ifconfig: {self._cfg.ifconfig}')
            if self._cfg.ifconfig[0] == 'dhcp':
                self._wlan.ifconfig('dhcp')
            elif len(self._cfg.ifconfig) == 4:
                self._wlan.ifconfig(self._cfg.ifconfig)
            else:
                self._cfg.ifconfig[0] = 'dhcp'
                self._cfg.save()
                reset()
        else:
            self._cfg.wlan_mode = network.AP_IF
            self._cfg.save()
            reset()

    @property
    def mode(self):
        return self._cfg.wlan_mode

    def is_connected(self):
        return self._wlan.isconnected()

    def scan(self):
        if self._scan == None or (utime.ticks_ms() - self._pre_time) > 30000:
            _wlan = self._wlan
            if self._cfg.wlan_mode != network.STA_IF:
                _wlan = network.WLAN(network.STA_IF)
                _wlan.active(True)
            elif self._wlan is None:
                self.init()
                _wlan = self._wlan

            self._scan = _wlan.scan()

            if self._cfg.wlan_mode != network.STA_IF:
                self.init()
            self._pre_time = utime.ticks_ms()

        return self._scan
    
    def ifconfig(self, ip = None, mask = None, gw = None, dns = None):
        if ip is None:
            return self._wlan.ifconfig()
        
        if ip is str and ip == "dhcp":
            # self._wlan.ifconfig('dhcp')
            return
        
        if ip is str and mask is str and gw is str and dns is str:
            self._wlan.ifconfig(ip, mask, gw, dns)
