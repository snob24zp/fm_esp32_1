#!/usr/bin/env python3
import sys
import serial
import re


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'{sys.argv[0]} [port] [file] [out_file]')
        exit(1)

    CMD = '''import os\r\n\r\n

with open("{0}","rb") as _fd:\r\n
r = _fd.read(1024)\r\n
while r:\r\n
print(r.hex())\r\n
r = _fd.read(1024)\r\n
\r\n
\r\n
\r\n
\r\n
\r\n'''.format(sys.argv[2]).encode('ascii')

    with serial.Serial(sys.argv[1], baudrate=115200, timeout=1) as ser:
        ser.write(CMD)
        ret = ''
        while True:
            r = ser.readall()
            if r:
                ret += r.decode('ascii')
            elif len(ret) > 0:
                break
    
    #print(ret[262:-18].strip('\r\n'))
    ret = ret[205:-18]
    ret = re.sub(r"[\n\t\s]*", "", ret)
    if len(sys.argv) > 3:
        with open(sys.argv[3], 'wb') as _fd:
            _fd.write(bytes.fromhex(ret))
    else:
        sys.stdout.buffer.write(bytes.fromhex(ret))


