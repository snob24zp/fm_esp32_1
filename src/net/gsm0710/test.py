import serial
import time

import ctypes as c
import pathlib
import threading

# to compile lib - `gcc -Wall -fdiagnostics-color=always -shared -fPIC -g unix.c gsm0710.c buffer.c -o gsm0710.so`

if __name__ == "__main__":
    # Load the shared library into ctypes
    libname = pathlib.Path().absolute() / "gsm0710.so"
    c_lib = c.CDLL(libname)
    with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser:
        @c.CFUNCTYPE(None, c.c_void_p, c.c_uint32)
        def on_fault(ctx, a):
            print('On fault: Line:',  a)

        @c.CFUNCTYPE(c.c_size_t, c.c_void_p, c.c_char_p, c.c_size_t)
        def write_sl(ctx, data: bytes, sz: int):
            print('Write slave:', data[:sz].hex('-'), sz)
            ser.write(data[:sz])
            return sz

        @c.CFUNCTYPE(None,c.c_void_p, c.c_uint8, c.c_char_p, c.c_size_t)
        def on_read_vl(ctx, port: int, data: bytes, sz: int):
            print('on read virtual:', port, data[:sz].hex('-'), sz, data[:sz].decode('ascii'))

        c_lib.set_on_fault(on_fault)
        c_lib.set_write_sl(write_sl)
        c_lib.set_on_read_vl(on_read_vl)

        ser.write(b'AT+CMUX=0\r\n')
        print(ser.read(1024))

        c_lib.init(3)

        def on_rx():
            while ser.is_open:
                data = ser.read(1024)
                if data:
                    print('--- RX data: ', data.hex('-'))
                    c_lib.on_read_serial(data, len(data))

        threading.Thread(target=on_rx, daemon=True).start()

        time.sleep(3)
        
        for i in range(1, 3):
            print(f'[{i}] -> AT')
            c_lib.write_virtual(i, b'AT\r\n', 4)
            time.sleep(1)

        time.sleep(5)
        c_lib.deinit()


