import os
import struct
import time
import sys
import base64

from uclient import aes
from log import log


if sys.version.count('MicroPython') > 0:
    import machine

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
        crc = crc ^ 0xFFFF
        return ((crc & 0xff) << 8) | (crc >> 8)

    def __init__(self, sig, offset, size, data) -> None:
        self.sig = sig
        self.offset = offset
        self.size = size
        self.data = data

    @staticmethod
    def parse(log, data: bytes):
        data = data.replace(b'\xba\x00', b'\xba')
        data = struct.unpack(">H528sH", data)
        if data[0] != 0xbabf:
            log.warn('Package have wrong header')
            return None

        if ueba_pkg.crc16(data[1]) != data[2]:
            log.warn('CRC1 missmatch')
            return None

        cipher = aes.cipher(ueba_pkg.FW_KEY, bytes(16))
        pkg = cipher.decrypt(data[1])

        data = struct.unpack(">HHIH6s512s", pkg)
        if ueba_pkg.DEV_TYPE != data[1]:
            log.warn('Signature missmatch')
            return None

        if ueba_pkg.crc16(pkg[2:]) != data[0]:
            log.warn('CRC2 missmatch')
            return None

        log.warn(f'Unpacked: {data[3]} bytes [@{data[2]:05x}]')
        return ueba_pkg(data[1], data[2], data[3], data[5][:data[3]])


class fwupd(log):
    FW_FILE = "fw.img"
    FW_MOUNTPOINT = "/upgrade"
    PG_SZ = 512

    def __init__(self) -> None:
        super().__init__('FW-UPD')
        self._is_not_simu = sys.version.count('MicroPython') > 0
        self.state = None
        self.reset()
        fwupd._mpy_cp()

    def reset(self):
        self.state = None
        self.info('Initialized')

    @staticmethod
    def isnumeric(inp):
        if isinstance(inp, str):
            return all([x >= '0' and x <= '9' for x in inp])
        elif isinstance(inp, (int, float)):
            return True
        else:
            return False

    @staticmethod
    def _mpy_cp():
        if sys.version.count('MicroPython') > 0 and fwupd.FW_FILE in os.listdir('.'):
            try:
                print(f"FW file size: {os.stat(fwupd.FW_FILE)[6]} bytes")
                print("Mount FS image")
                os.mount(fwupd.FW_FILE, fwupd.FW_MOUNTPOINT)
                print('Copying. Disk free: ', disk.free('/'))
                sz = os.cp(fwupd.FW_MOUNTPOINT, '.', True)
                print(f'Copy done: {sz} bytes')
                print('Unmounting disk. Disk free:', disk.free('/'))
                os.umount(fwupd.FW_MOUNTPOINT)
            finally:
                print('Unlink FW disk image')
                os.unlink(fwupd.FW_FILE)
                print('Reseting in 10s')
                time.sleep(10)
                machine.reset()

    def fwupd(self, cmd):
        if not fwupd.isnumeric(cmd):
            return 'Command should be numeric'

        if int(cmd) == 0:
            self.reset()
            return 'OK'

        if int(cmd) == 1:
            self.reset()
            self.state = 1
            self.warn('Prepared to upgrade')
            return 'OK'

        if int(cmd) == 2 and self.state == 1:
            self.warn('Try to mount incoming FW-image')
            try:
                if sys.version.count('MicroPython') > 0:
                    os.mount(fwupd.FW_FILE, fwupd.FW_MOUNTPOINT)
                else:
                    time.sleep(1)
                self.warn('Mounting done. Image valid')
                self.state = 2
                return 'OK'
            except Exception as ex:
                self.err(str(ex))
                self.state = 0
                os.unlink(fwupd.FW_FILE)
                return "Error"
        elif int(cmd) == 3 and self.state == 2:
            if sys.version.count('MicroPython') > 0:
                machine.Timer(-1, period=1000, mode=machine.Timer.ONE_SHOT, callback=lambda t: machine.reset())
            return 'OK'
        else:
            self.reset()
            return 'Wrong state or command for state'

    def fwpkg(self, pkg):
        if self.state == 1:
            pkg = base64.b64decode(pkg)
            self.warn(f'Recieved {len(pkg)} data')
            pkg = ueba_pkg.parse(self, pkg)
            if pkg is not None:
                idx = pkg.offset // fwupd.PG_SZ
                s = time.time_ns()
                with open(fwupd.FW_FILE, 'wb' if idx == 0 else 'r+b') as fd:
                    fd.seek(pkg.offset)
                    fd.write(pkg.data)

                self.warn(f'Writing {idx} done@{pkg.offset} ({(time.time_ns() - s) // 10e6} ms)')

                return {"chunk": idx + 1}
        return {"error": "Wrong state", "chunk": 0}
