
import os
from fwupd import fwupd, ueba_pkg

import mrequests
from threadmpy import start_thread
import base64

from uclient.device import device_base
from uclient.evtdev import event_device

class fwupd_device(event_device, fwupd):
    ALLOWED_HOSTS_FILE = 'data/fwupd.hosts'
    UEBA_FW = 'fw.uebf'

    def __init__(self, serial: int, dtype:int=device_base.DEVICE_TYPE, regs: dict={}, status: int=0, device_id : bytes = None) -> None:
        super().__init__(serial, dtype, regs, status, device_id)
        super(device_base, self).__init__()
        self.dl_run = 0
        
    def dl(self, url, topic):
        resp = mrequests.get(url)
        self.info(f"Resp: {url} -> {resp.status_code}")
        with open(fwupd_device.UEBA_FW, 'wb') as fd:
            sz = 1
            total = 0
            while sz and self.dl_run:
                data = resp.read(fwupd.PG_SZ)
                sz = len(data)
                if sz:
                    fd.write(data)
                    total += sz
                    self.info(f"Downloaded: {total}")
                    self.pub_dev(topic, total)
    
    def convert(self):
        with open(fwupd_device.UEBA_FW, 'rt') as fd:
            idx = 0
            rest = ""
            while True:
                data = rest + fd.read(1024)
                start_idx = data.find("<chunk>") + len("<chunk>")
                if start_idx == -1:
                    break

                stop_idx = data.find("</chunk>")
                if stop_idx == -1:
                    data += fd.read(1024)
                
                stop_idx = data.find("</chunk>")
                if stop_idx == -1:
                    break

                rest = data[stop_idx + len("</chunk>"):]
                data = data[start_idx:stop_idx]

                self.info(f'Decrypt {idx} chunk')
                data = base64.b64decode(data)
                pkg = ueba_pkg.parse(self, data)
                if pkg is not None:
                    idx = pkg.offset // fwupd.PG_SZ
                    with open(fwupd.FW_FILE, 'wb' if idx == 0 else 'r+b') as out_fd:
                        out_fd.seek(pkg.offset)
                        out_fd.write(pkg.data)
                        idx += 1
                else:
                    break

    def dl_thr(self, topic, url):
        try:
            self.info(f"Downloading: {url}")
            self.dl(url, topic)
            self.convert()
            os.unlink(fwupd_device.UEBA_FW)
            self.pub_dev(topic, "OK")
            self.state = 1
        except OSError as ex:
            self.err(f'Downloading failed: {str(ex)}')

    def hnd_msg(self, topic, msg):
        if topic == 'fw_upd':
            if msg == 0:
                self.dl_run = 0

            self.pub_dev(topic, self.fwupd(msg))
            return
        if topic == 'fw_pkg':
            self.pub_dev(topic, self.fwpkg(msg))
            return
        if topic == 'fw_url':
            allow = False
            try:
                with open(fwupd_device.ALLOWED_HOSTS_FILE, 'rt') as fd:
                    for host in fd.readlines():
                        if msg.startswith(host):
                            allow = True
                            break
            except OSError:
                pass
            
            if not allow:
                self.err('Downloading FW-Update is forbiden')
                return
            
            self.dl_run = 1
            start_thread(self.dl_thr, (topic, msg))

        return super().hnd_msg(topic, msg)