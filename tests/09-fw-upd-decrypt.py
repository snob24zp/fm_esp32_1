#!/usr/bin/python3

import os
import unittest
import xmlrunner
import unittest
import xml.etree.ElementTree as xml_parser


import sys
path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(path)
sys.path.append(f'{path}{os.path.sep}src')
sys.path.append(f'{path}{os.path.sep}src{os.path.sep}uclient')

import fwupd

class fwupd_decrypt_test(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.assertTrue(os.system('./fwupd.sh') == 0)
        with open('out/fw.fs', 'rb') as fd:
            self.ref = fd.read()

        self.chunks = []
        _in = None
        with open('out/AR.FW.latest.uebf', 'rb') as fd:
            _in = fd.read()
        fw_root = xml_parser.fromstring(_in)
        
        for chunk in fw_root.find("chunks"):
            self.chunks.append(chunk.text)

    def decrypt_tst(self):
        fw = fwupd.fwupd()
        fw.fwupd("1")
        ch_len = fwupd.fwupd.PG_SZ
        for idx, _chunk in enumerate(self.chunks):
            print(f'feed: {idx}')
            fw.fwpkg(_chunk)
            
        fw.fwupd("2")
        fw.fwupd("3")
        
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
            ref = self.ref[idx * ch_len:][:ch_len]
            self.assertTrue(len(dec) == len(ref))
            self.assertTrue(dec == ref)
        
        os.unlink('fw.img')

    def test(self):
        self.decrypt_tst()


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(),"out/tests")))
