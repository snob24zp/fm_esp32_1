import os

class fat_bdev:
    def __init__(self, filename, blocksize = 512):
        self.block_size = blocksize
        self.filename = filename
        self.block_count = os.stat(self.filename)[6] // self.block_size

    def readblocks(self, block_num, buf, offset=0):
        addr = block_num * self.block_size + offset
        with open(self.filename, 'rb') as fd:
            fd.seek(addr)
            fd.readinto(buf)

    def writeblocks(self, block_num, buf, offset=0):
        addr = block_num * self.block_size + offset
        with open(self.filename, 'r+b') as fd:
            fd.seek(addr)
            fd.write(buf)

    def ioctl(self, op, arg):
        if op == 4: # block count
            return self.block_count
        if op == 5: # block size
            return self.block_size
        if op == 6: # block erase
            addr = arg * self.block_size
            with open(self.filename, 'r+b') as fd:
                fd.seek(addr)
                fd.write(bytes(512))
            return 0
        
def cp(fnamea, fnameb):
    with open(fnamea, 'r') as fda:
        with open(fnameb, 'w') as fdb:
            total = 0
            ret = 512
            while ret:
                buf = bytearray(512)
                ret = fda.readinto(buf)
                total += ret
                fdb.write(buf[:ret])
            return total
        
def rm(fname):
    os.unlink(fname)
    
def mv(fnamea, fnameb):
    cp(fnamea, fnameb)
    rm(fnamea)

def mount(fname, path):
    os.mount(fat_bdev(fname), path)

def umount(path):
    os.umount(path)

def cat(fname):
    with open(fname, 'rb') as fd:
        return fd.read()

def tee(fname, data, offset = 0):
    with open(fname, 'r+b') as fd:
        if offset > 0:
            fd.seek(offset)
        return fd.write(data)

def free(path):
    ret = os.statvfs(path)
    return (ret[0] * ret[3]), (ret[0] * ret[2]) 

def format(_f):
    import machine
    for idx in range(_f.ioctl(4, 0)):
        print(f'Erase: {idx} page', _f.ioctl(6, idx) == 0)
    machine.reset()