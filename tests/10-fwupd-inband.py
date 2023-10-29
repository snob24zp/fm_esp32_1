#!/usr/bin/python3


import sys
import os
import unittest
import xmlrunner
import xml.etree.ElementTree as xml_parser

from config import config_t
from uclient.fwupd import fwupd_device
from fwupd import fwupd
try:
    from tests.test_tpl import test_tpl
except ImportError:
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.append(path)
    from test_tpl import test_tpl


class fwupd_inband_test(test_tpl):

    def setUp(self):
        super().setUp(dtype=fwupd_device)
        with open('out/fw.fs', 'rb') as fd:
            self.ref = fd.read()
        self.chunks = []
        _in = None
        with open('out/AR.FW.latest.uebf', 'rb') as fd:
            _in = fd.read()
        fw_root = xml_parser.fromstring(_in)
        
        for chunk in fw_root.find("chunks"):
            self.chunks.append(chunk.text)
        self.state = 0
        self.resp = None
        self.next_chunk = 0

    def on_fwupd(self, topic, msg):
        print('FW-UPD: ', msg)
        self.resp = str(msg)

    def on_fwpkg(self, topic, msg):
        print('FW-PKG: ', msg)
        self.next_chunk = msg['chunk']

    def test(self):
        self.subscribe_device('fw_upd', self.on_fwupd)
        self.subscribe_device('fw_pkg', self.on_fwpkg)
        self.publish_device('fw_upd', 1)
        self.wait_condition(lambda: self.resp is not None, 10)
        self.resp = None
        while self.next_chunk < len(self.chunks):
            self.publish_device('fw_pkg', self.chunks[self.next_chunk])
            cur = self.next_chunk
            self.wait_condition(lambda: cur != self.next_chunk, 10) # let's think that we have an ideal network

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

        print(len(decrypted))
        self.assertTrue(len(decrypted) == len(self.chunks))

        for idx in range(len(decrypted)):
            dec = decrypted[idx]
            ref = self.ref[idx * 512:][:512]
            self.assertTrue(len(dec) == len(ref))
            self.assertTrue(dec == ref)

        os.unlink('fw.img')





if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(),"out/tests")))
