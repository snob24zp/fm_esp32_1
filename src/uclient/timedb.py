
import time
import os
import sys
import json
import struct

def _get_tm():
    if hasattr(time, 'ticks_ms'):
        return time.ticks_ms()
    else:
        return int(time.time() * 1000)

class tbl_item_t:
    EVT_FMT = '>QLL'
    def __init__(self, pos: int, sz: int, tm: int = 0) -> None:
        self.tm = (time.mktime(time.localtime()) + 946684800) if tm == 0 else tm
        if sys.platform == 'linux' and tm == 0:
            self.tm = _get_tm()

        self.sz = sz
        self.pos = pos

    @staticmethod
    def itm_sz():
        return struct.calcsize(tbl_item_t.EVT_FMT)

    @staticmethod
    def parse(raw: bytes):
        (tm, pos, sz) = struct.unpack(tbl_item_t.EVT_FMT, raw[:tbl_item_t.itm_sz()])
        return tbl_item_t(pos, sz, tm)

    def serialize(self):
        return struct.pack(tbl_item_t.EVT_FMT, self.tm,self.pos, self.sz)

    def __repr__(self) -> str:
        return f'item@{self.tm} [ at: {self.pos} sz: {self.sz}]]'

    def __str__(self) -> str:
        return self.__repr__()

class tbl_t:
    TBL_SZ = 1024
    MEM_DIR = 'data'
    FNAME = '%s.dat'
    TBLNAME = '%s.tbl'
    
    def __init__(self, db_name: str, max_sz = TBL_SZ) -> None:
        self.__db_name = db_name
        self.__max_sz = max_sz

        if not tbl_t.MEM_DIR in os.listdir('.'):
            os.mkdir(tbl_t.MEM_DIR)

    @property
    def tblname(self):
        return tbl_t.TBLNAME % self.__db_name
    
    @property
    def tblpath(self):
        return f'{tbl_t.MEM_DIR}/{tbl_t.TBLNAME % self.__db_name}'
    
    @property
    def datapath(self):
        return f'{tbl_t.MEM_DIR}/{tbl_t.FNAME % self.__db_name}'
    
    
    @property
    def dataname(self):
        return tbl_t.FNAME % self.__db_name

    def push(self, obj: object, tm: int = 0):
        dat = f'{json.dumps(obj)}\r\n'.encode('utf-8')
        # dat = zlib.compress(dat)
        mdf = 'ab'
        if not self.tblname in os.listdir(tbl_t.MEM_DIR):
            mdf = 'wb'
        else:
            sz = os.stat(self.tblpath)[6]
            if sz >= self.__max_sz * tbl_item_t.itm_sz():
                mdf = 'wb'
                if f'{self.tblname}.1' in os.listdir(tbl_t.MEM_DIR):
                    os.unlink(f'{self.tblpath}.1')
                os.rename(self.tblpath, f'{self.tblpath}.1')

                if f'{self.dataname}.1' in os.listdir(tbl_t.MEM_DIR):
                    os.unlink(f'{self.datapath}.1')
                os.rename(self.datapath, f'{self.datapath}.1')

        with open(self.tblpath, mdf) as fd:
            sz =  0 if not self.dataname in os.listdir(tbl_t.MEM_DIR) else os.stat(self.datapath)[6]
            fd.write(tbl_item_t(sz, len(dat), tm).serialize())

        with open(self.datapath, mdf) as fd:
            fd.write(dat)
            
    def at(self, idx, volume = 0):
        if volume == 0:
            tbl = self.tblpath
            datf = self.datapath
        else:
            tbl = f'{self.tblpath}.{volume}'
            datf = f'{self.datapath}.{volume}'
        
        sz = os.stat(tbl)[6] // tbl_item_t.itm_sz()
        if idx >= sz:
            return None, None

        with open(tbl, 'rb') as fd:
            fd.seek(idx * tbl_item_t.itm_sz())
            evt = tbl_item_t.parse(fd.read())
            with open(datf, 'rb') as data_fd:
                data_fd.seek(evt.pos)
                return evt, json.loads(data_fd.read(evt.sz).decode())
    
    def fisrt(self):
        return self.at(0, 1)
    
    def last(self):
        sz = os.stat(self.tblpath)[6] // tbl_item_t.itm_sz()
        return self.at(sz - 1, 0)

    def search(self, tm, nearest = False, volume = 0):
        if volume == 0:
            tbl = self.tblpath
        else:
            tbl = f'{self.tblpath}.{volume}'
        
        sz = 0
        try:
            sz = os.stat(tbl)[6] // tbl_item_t.itm_sz()
        except:
            if nearest and volume != 0: # kostyl'
                tm = self.at(0, 0)
                return 0, tm[0], tm[1]
            else:
                return None

        ptr = sz // 2

        if self.at(0, volume)[0].tm > tm:
            return self.search(tm, nearest, volume + 1)
        
        step = ptr // 2
        while True:
            evt, data = self.at(ptr, volume)
            if evt is None:
                break
            if tm < evt.tm:
                ptr -= step
            elif tm > evt.tm:
                ptr += step
            else:
                return ptr, evt, data
            
            if step == 0:
                if nearest:
                    return ptr, evt, data
                return None
            step >>= 1



def test_int():
    import random

    total_tm = _get_tm()
    try:
        os.unlink('data/test-db.dat')
        os.unlink('data/test-db.dat.1')
        os.unlink('data/test-db.tbl.1')
        os.unlink('data/test-db.tbl')
        print(f'Removing old db is done: {_get_tm() - total_tm}')
    except:
        print("Device doesn't have DB")

    db_items = 1536
    db = tbl_t('test-db')
    for _ in range(db_items):
        _evt_tm = _get_tm()
        tm = _get_tm()
        evt = random.randint(0, 2 ** 30)
        db.push(evt, _evt_tm)
        print(f'({(_get_tm() - tm):.2f} mS) Push: {evt}')

    print('-------------------------------------------------------------')
    print(f'Test pass. Elapsed: {_get_tm() - total_tm} mS')


def test():
    import random
    import base64
    
    total_tm = _get_tm()
    try:
        os.unlink('data/test-db.dat')
        os.unlink('data/test-db.dat.1')
        os.unlink('data/test-db.tbl.1')
        os.unlink('data/test-db.tbl')
        print(f'Removing old db is done: {_get_tm() - total_tm}')
    except:
        print("Device doesn't have DB")

    db_items = 1536
    db = tbl_t('test-db')
    search_rnd = random.randint(0, db_items)
    search_evt = None
    for idx in range(db_items):
        _evt_tm = _get_tm()
        rnd_b = bytes([ random.randrange(0xff) for _ in range(random.randrange(32)) ])
        evt = {'idx': idx, 'tm': _evt_tm, 'data': base64.b64encode(rnd_b).decode() }
        if idx == search_rnd:
            search_evt = evt

        tm = _get_tm()
        db.push(evt, _evt_tm)
        print(f'({(_get_tm() - tm):.2f} mS) Push: {evt}')

    tm = _get_tm()
    found_evt = db.search(search_evt["tm"])
    print(f'({_get_tm() - tm:.4f} mS) Searching: {search_evt}. Found: {found_evt}')
    assert(search_evt['tm'] == found_evt[1].tm)

    tm = _get_tm()
    rnd_tm = random.randint(db.fisrt()[0].tm, db.last()[0].tm)
    rnd_evt = db.search(rnd_tm,True)
    print(f'({_get_tm() - tm:.4f} mS) Nearest to: {rnd_tm}. Found: {rnd_evt}')
    assert(rnd_evt[1].tm < rnd_tm + 2000 and rnd_evt[1].tm > rnd_tm - 2000)
    
    rnd_evt = db.search(1234)
    assert(rnd_evt is None)

    print('-------------------------------------------------------------')
    print(f'Test pass. Elapsed: {_get_tm() - total_tm} mS')

if __name__ == '__main__':
    test()
    
    