#!/usr/bin/python3


import os
import unittest
import xmlrunner

import sys
path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(path)
sys.path.append(f'{path}{os.path.sep}src')
sys.path.append(f'{path}{os.path.sep}src{os.path.sep}uclient')


from uclient.fwupd import fwupd_device
from fwupd import fwupd
try:
    from tests.test_tpl import test_tpl
except ImportError:
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(path)
    from test_tpl import test_tpl


class fwupd_outband_test(test_tpl):
    FW_URL = "https://release.dlab.pw/esp32-mpy-uclient/AR.FW.latest.uebf"

    def setUp(self):
        super().setUp(dtype=fwupd_device)
        os.system('./fwupd.sh')
        os.system('scp ./out/AR.FW.latest.uebf root@dlab.pw:/var/www/release/')
        with open('out/fw.fs', 'rb') as fd:
            self.ref = fd.read()

        self.state = 0
        self.resp = None
        self.dl_sz = 0

    def on_fwupd(self, topic, msg):
        print('FW-UPD: ', msg)
        self.resp = str(msg)

    def on_fwurl(self, topic, msg):
        print('FW-URL: ', msg)
        self.dl_sz = msg

    def test(self):
        with open(fwupd_device.ALLOWED_HOSTS_FILE, 'wt') as fd:
            fd.writelines(['https://release.dlab.pw'])

        self.subscribe_device('fw_upd', self.on_fwupd)
        self.subscribe_device('fw_url', self.on_fwurl)
        
        self.publish_device('fw_url', fwupd_outband_test.FW_URL)
        self.wait_condition(lambda: self.dl_sz == "OK", 60)

        self.publish_device('fw_upd', 2)
        self.wait_condition(lambda: self.resp is not None, 10)
        self.resp = None

        self.publish_device('fw_upd', 3)
        self.wait_condition(lambda: self.resp is not None, 10)
        self.resp = None
        
        ch_len = fwupd.PG_SZ
        print(f'Chunk len: {ch_len}')
        decrypted = []
        with open('fw.img', 'rb') as fd:
            ret = fd.read(ch_len)
            while ret:
                decrypted.append(ret)
                ret = fd.read(ch_len)

        for idx in range(len(decrypted)):
            dec = decrypted[idx]
            ref = self.ref[idx * 512:][:512]
            self.assertTrue(len(dec) == len(ref))
            self.assertTrue(dec == ref)

        os.unlink('fw.img')





if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(),"out/tests")))
