
from uclient import hub
import base64
from ucryptolib import aes


class fwupd:
    ERR_MAX_CNT = 10

    class __fw_pkt:
        def __init__(self, data: bytes) -> None:
            self.raw = data
            self.raw_hdr = data[:16]
            self.crc = int.from_bytes(data[0:2], 'little')
            self.signature = int.from_bytes(data[2:4], 'big')
            self.offset = int.from_bytes(data[4:8], 'big')
            self.payload = data[16:]

    def __init__(self, client: hub, deckey: bytes) -> None:
        '''
        :param ucl: Uclient instance
        '''
        self.__client = client
        self.__client.set_on_fw_upd(self.__on_fw_upd)
        self.__client.set_on_fw_pkg_push(self.__on_fw_pkg)
        self.__cur_chunk = 0
        self.__deckey = base64.b64decode(deckey)
        self.__err_cnt = 0
        self.__fwfile = None
        self.__on_done_cb = None

    def __on_fw_upd(self, dev: dict, cmd: int):

        if cmd == 1:
            self.__cur_chunk = 0
            self.__err_cnt = 0
            self.__fwfile = open(f'', 'wt') #tempfile.NamedTemporaryFile()
            return 0

        if cmd == 2:
            self.__fwfile.flush()

            # with zipfile.ZipFile(self.__fwfile.name, 'r') as zip_ref:
            #     path = os.path.dirname(os.path.realpath(sys.argv[0]))
            #     zip_ref.extractall(path)

            self.__fwfile.close()
            return 0

        if cmd == 3:
            ret = True
            if self.__on_done_cb is not None and callable(self.__on_done_cb):
                ret = self.__on_done_cb()

            if ret:
                print('success')
                # sys.stdout.flush()
                # subprocess.Popen(sys.argv)
                # sys.exit(0)

            self.__client.dereg()
            return 0

    def __on_fw_pkg(self, dev: dict, data: bytes):
        if self.__fwfile is None:
            return -1

        data = fwupd.__get_raw_pkg(data)
        if data is None:
            if self.__err_cnt < self.ERR_MAX_CNT:
                self.__err_cnt += 1
                return self.__cur_chunk
            else:
                raise IOError('wrong incoming data (outer crc mismatch)')

        hdr = fwupd.__fw_pkt(fwupd.__decrypt(bytes(data), self.__deckey))
        self.__fwfile.write(hdr.payload)

        self.__cur_chunk += 1
        return self.__cur_chunk

    @staticmethod
    def __decrypt(data: bytes, key: bytes, iv=bytes(16)):
        cipher = aes(key, 2, iv)
        return cipher.decrypt(data)

    @staticmethod
    def __get_raw_pkg(data: bytes):
        data = fwupd.__rm_ba_frame(data)
        _in_crc = int.from_bytes(data[-2:], 'little')
        data = data[:-2]
        if _in_crc != fwupd.crc16(data):
            return None
        return data

    @staticmethod
    def crc16(data: bytearray, offset: int = 0, length: int = 0):
        if length == 0:
            length = len(data)

        if data is None or offset < 0 or offset > len(data) - 1 and offset+length > len(data):
            return 0
        crc = 0xffff
        for i in range(0, length):
            crc ^= data[offset + i]
            for j in range(0, 8):
                if (crc & 1) > 0:
                    crc = (crc >> 1) ^ 0x8408
                else:
                    crc = crc >> 1
        crc = 0xffff - crc
        return crc

    @staticmethod
    def __rm_ba_frame(data: bytearray):
        d = bytearray()
        while len(data):
            if data[0] == 0xba:
                if data[1] == 0:
                    d.append(0xba)
                data = data[1:]
            else:
                d.append(data[0])
            data = data[1:]

        return d

    def set_on_done(self, cb):
        if callable(cb):
            self.__on_done_cb = cb
