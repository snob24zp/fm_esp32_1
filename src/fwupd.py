import uclient.aes as aes
import base64
from log import log
import disk
import os
import struct
import time

import sys

if sys.version.count('MicroPython') > 0:
    from machine import reset, Timer
else:
    def reset():
        exit(0)


class ueba_pkg:
    DEV_TYPE = 5523
    FW_KEY = b'\x8f\x1a\x12\x81\xc6\x9e\x07\x9f\x9a\x06\xb8.\xf7\x94_I'

    PRESET = 0xFFFF
    POLYNOMIAL = 0x8408  # bit reverse of 0x8005

    @staticmethod
    def crc16(data):
        crc = ueba_pkg.PRESET
        for c in data:
            crc = crc ^ c
            for j in range(8):
                if (crc & 1) == 0:
                    crc = crc >> 1
                else:
                    crc = crc >> 1
                    crc = crc ^ ueba_pkg.POLYNOMIAL
        crc =  crc ^ 0xFFFF
        return ((crc & 0xff) << 8) | (crc >> 8)

    def __init__(self, sig, offset, size, data) -> None:
        self.sig = sig
        self.offset = offset
        self.size = size
        self.data = data

    @staticmethod
    def parse(log, data: bytes):
        data = data.replace(b'\xba\x00', b'\xba')
        pkg = struct.unpack(">H528sH", data)
        if pkg[0] != 0xbabf:
            log.warn('Package have wrong header')
            return None

        if ueba_pkg.crc16(pkg[1]) != pkg[2]:
            log.warn('CRC1 missmatch')
            return None

        cipher = aes.cipher(ueba_pkg.FW_KEY, bytes(16))
        pkg = cipher.decrypt(pkg[1])
        
        
        data = struct.unpack(">HHIH6s512s", pkg)
        if ueba_pkg.DEV_TYPE != data[1]:
            log.warn('Signature missmatch')
            return None
        
        if  ueba_pkg.crc16(pkg[2:]) != data[0]:
            log.warn('CRC2 missmatch')
            return None

        log.warn(f'Unpacked: {data[3]} bytes')
        return ueba_pkg(data[1], data[2], data[3], data[5][:data[3]])


class fwupd(log):
    FW_FILE = "fw.img"
    FW_MOUNTPOINT = "/upgrade"

    def __init__(self) -> None:
        super().__init__('FW-UPD')
        self.fd = None
        self.reset()

    def reset(self):
        self.state = None
        self.idx = 0
        if self.fd is not None:
            self.fd.close()
        self.fd = None
        self.info('Initialized')

    @staticmethod
    def isnumeric(inp):
        return all([x >= '0' and x <= '9' for x in inp])

    def fwupd(self, cmd):

        if not fwupd.isnumeric(cmd):
            return 'Command should be numeric'

        if int(cmd) == 1 and self.state == None:
            self.reset()
            self.state = 1
            self.fd = open(fwupd.FW_FILE, 'wb')
            self.warn('Prepared to upgrade')
            return 'OK'
        elif int(cmd) == 2 and self.state == 1:
            self.fd.close()
            self.warn('Try to mount incoming FW-image')
            if sys.version.count('MicroPython') > 0:
                disk.mount(fwupd.FW_FILE, '/upgrade')
            else:
                time.sleep(1)
            self.warn('Mounting done')
            self.state = 2
            return 'OK'
        elif int(cmd) == 3 and self.state == 2:
            def _mpy_cp():
                self.warn('Copying files')
                sz = disk.cp(fwupd.FW_MOUNTPOINT, '.', True)
                self.warn(f'Copied: {sz} bytes')
                os.unlink(fwupd.FW_FILE)
                reset()

            if sys.version.count('MicroPython') > 0:
                Timer(-1,period=100, mode=Timer.ONE_SHOT, callback=_mpy_cp)
            return 'OK'
        else:
            self.reset()
            return 'Wrong state or command for state'

    def fwpkg(self, pkg):
        if self.state == 1 and self.fd:
            chunk = base64.b64decode(pkg)
            self.warn(f'Recieved {len(chunk)} data')
            ret = ueba_pkg.parse(self, chunk)
            if ret is not None:
                self.fd.seek(ret.offset)
                self.fd.write(ret.data)
                self.idx += 1
                return {"chunk": self.idx }
        return {"error": "Wrong state", "chunk": 0 }
