import board
from machine import unique_id, Timer, reset
from microdot import Microdot, send_file
from config import config_t
from version import STATIC_VERSION



def init():
    webserv = Microdot()

    @webserv.route('/')
    def root_hnd(req):
        return send_file('/static/index.html')

    @webserv.route('/info', methods=['GET'])
    def info_hnd(req):
        uid = unique_id()
        mac = uid.hex(':')
        ifconfig = board.network.ifconfig()
        return {
            "mac": f"{mac}",
            "version": f"{STATIC_VERSION}",
            "type": f"AR-{uid.hex()}",
            "serial": int.from_bytes(uid[3:], 'big'),
            "ip_type": 0 if len(config_t().ifconfig) == 4 else 1,
            "ip": ifconfig[0],
            "mask": ifconfig[1],
            "gw": ifconfig[2],
            "dns": ifconfig[3]
            }

    @webserv.route('/ap_list', methods=['GET'])
    def ap_list_hnd(req):
        if hasattr(board.network, 'scan'):
            _ap_list = board.network.scan()
            return [bytes.decode(x[0]) for x in _ap_list]
        else:
            return []


    @webserv.route('/ctrl', methods=['POST'])
    def ctrl_hnd(req):
        _cfg = config_t()
        if "ap" in req.json and "password" in req.json:
            _cfg.sta_ssid = req.json['ap']
            _cfg.sta_pwd = req.json['password']
            _cfg.wlan_mode = 0 # sta
        
        if "server" in req.json:
            _cfg.server = req.json['server']
        if "token" in req.json:
            _cfg.token = req.json['token']
            
        if "ip_type" in req.json:
            if "ip" in req.json and "mask" in req.json and "gw" in req.json and "dns" in req.json and req.json['ip_type'] == 0:
                _cfg.ifconfig = (req.json['ip'], req.json['mask'], req.json['gw'], req.json['dns'])
            elif req.json['ip_type'] == 1:
                _cfg.ifconfig = ('dhcp',)

        _cfg.save()
        Timer(0,period=1000, mode=Timer.ONE_SHOT, callback=lambda t:reset())
        return "\"OK\""


    @webserv.route('/<file>', methods=['GET'])
    def file_hnd(req, file):
        if '..' in file:
            return 'Not found', 404

        return send_file('static/' + file, max_age=86400)
    
    return webserv
