import board
from machine import unique_id, Timer, reset
from microdot import Microdot, send_file
from hw.wlan import WLAN
from config import config_t


VERSION = 'R230620;master;853757db52ef99c85ddf706c47973870aa1d4263'

wlan = WLAN()
webserv = Microdot()

@webserv.route('/')
def root_hnd(req):
    return send_file('/static/index.html')


@webserv.route('/info', methods=['GET'])
def info_hnd(req):
    uid = unique_id()
    mac = uid.hex(':')
    return {"mac": f"{mac}", "version": f"{VERSION}", "type": f"AR-{uid.hex()}", "serial": int.from_bytes(uid[3:], 'big')}


@webserv.route('/ap_list', methods=['GET'])
def ap_list_hnd(req):
    global wlan
    _ap_list = wlan.scan()
    return [bytes.decode(x[0]) for x in _ap_list]


@webserv.route('/ctrl', methods=['POST'])
def ctrl_hnd(req):
    _cfg = config_t()
    _cfg.sta_ssid = req.json['ap']
    _cfg.sta_pwd = req.json['password']
    
    _cfg.server = req.json['server']
    _cfg.token = req.json['token']
    _cfg.wlan_mode = 0 # sta
    _cfg.save()
    Timer(0,period=1000, mode=Timer.ONE_SHOT, callback=lambda t:reset())
    return "\"OK\""


@webserv.route('/<file>', methods=['GET'])
def file_hnd(req, file):
    if '..' in file:
        return 'Not found', 404

    return send_file('static/' + file, max_age=86400)


def main():
    global webserv
    webserv.run(port=80, debug=True)


if __name__ == '__main__':
    main()
