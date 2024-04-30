import board
import sys
from net.microdot import Microdot, send_file
from config import config_t
from log import log
from version import STATIC_VERSION
from fwupd import fwupd
import json


if sys.version.count('MicroPython') > 0:
    from micropython import const
    from machine import Timer, reset
else:
    import os
    import time

    def const(d):
        return d

    def reset():
        exit(0)

def init():
    global webserv
    _log = log('WEBAPP')
    _fwupd = fwupd()
    webserv = Microdot()

    @webserv.route('/')
    def root_hnd(req):
        _log.info('GET /')
        return send_file('./static/index.html')

    @webserv.route('/info', methods=['GET'])
    def info_hnd(req):
        _log.info('GET /info')
        cfg = config_t()
        ifconfig = board.network.ifconfig()
        return {
            "mac": f"{cfg.token}",
            "version": f"{STATIC_VERSION}",
            "type": f"AR-{cfg.mac}",
            "serial": int.from_bytes(bytes.fromhex(cfg.mac)[3:], 'big'),
            "ip_type": 0 if len(cfg.ifconfig) == 4 else 1,
            "ip": ifconfig[0],
            "mask": ifconfig[1],
            "gw": ifconfig[2],
            "dns": ifconfig[3]
        }

    @webserv.route('/ap_list', methods=['GET'])
    def ap_list_hnd(req):
        _log.info('GET /ap_list')
        if hasattr(board.network, 'scan'):
            _ap_list = board.network.scan()
            return [bytes.decode(x[0]) for x in _ap_list]
        else:
            return []

    @webserv.route('/ctrl', methods=['POST'])
    def ctrl_hnd(req):
        _log.info(f'POST /ctrl ({req.json})')
        _cfg = config_t()
        if "ap" in req.json and "password" in req.json:
            _cfg.sta_ssid = req.json['ap']
            _cfg.sta_pwd = req.json['password']
            _cfg.wlan_mode = 0  # sta

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
        _log.warn('Going to reboot in 1s')
        if sys.version.count('MicroPython') > 0:
            reset()
            # Timer(-1, period=1000, mode=Timer.ONE_SHOT, callback=lambda t: reset())
        return "\"OK\""

    @webserv.route('/fw_upd', methods=['POST'])
    def fwupd_hnd(req):
        _log.info(f'POST /fw_upd ({req.json})')
        if req.body.decode() == 3:
            webserv.shutdown()
        return json.dumps(_fwupd.fwupd(req.body.decode()))

    @webserv.route('/fw_pkg', methods=['POST'])
    def fwupd_hnd(req):
        _log.info(f'POST /fw_pkg')
        ret = _fwupd.fwpkg(req.body.decode())
        if "error" in ret:
            return json.dumps(ret), 500
        return json.dumps(ret)

    @webserv.route('/reset', methods=['POST'])
    def fwupd_hnd(req):
        _log.warn(f'POST /reset ({req.json})')
        return "OK"

    @webserv.route('/<file>', methods=['GET'])
    def file_hnd(req, file):
        _log.info(f'GET /{file}')
        if '..' in file:
            return 'Not found', 404

        return send_file('./static/' + file, max_age=86400)

    _log.info('init done')
    return webserv
