import os
import select

def test2():
    ms, sl = os.openpty()
    print(os.ttyname(sl))
    while True:
        _fd,_,_ = select.select([ms],[],[])
        if len(_fd) > 0:
            cmd = os.read(_fd[0], 1024)
            print(cmd.decode())
            os.write(ms, b'OK\r\n')
            if cmd.decode().lower() == 'e':
                break


if __name__ == "__main__":
    test2()

