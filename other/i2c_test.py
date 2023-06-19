from contextlib import contextmanager
from fcntl import ioctl
from io import BufferedWriter
import time


I2C_SLAVE = 0x0703

_GPIO_VAL = 0


LOW = 0
HIGH = 1

HALF_STEP = [
    [LOW, HIGH, HIGH, HIGH],
    [LOW, LOW, HIGH, HIGH],
    [HIGH, LOW, HIGH, HIGH],
    [HIGH, LOW, LOW, HIGH],
    [HIGH, HIGH, LOW, HIGH],
    [HIGH, HIGH, LOW, LOW],
    [HIGH, HIGH, HIGH, LOW],
    [LOW, HIGH, HIGH, LOW],
]


def write_reg(dev: BufferedWriter, reg: int, data: bytes):
    dev.write(bytes([reg & 0xff, *data]))


def set_gpio(i2cdev, io, val):
    global _GPIO_VAL
    if val:
        _GPIO_VAL |= (1 << io)
    else:
        _GPIO_VAL &= ~(1 << io)
    write_reg(i2cdev, _GPIO_VAL, bytes())


@contextmanager
def get_i2cdev(i2cnum: int, addr: int = 0x38):
    i2cdev = open(f'/dev/i2c-{i2cnum}', 'wb')
    if ioctl(i2cdev, I2C_SLAVE, addr) != 0:
        raise IOError('PCF8574A not found')
    try:
        yield i2cdev
    finally:
        i2cdev.close()


def step(i2cdev, count, direction=1):
        """Rotate count steps. direction = -1 means backwards"""
        for x in range(count):
            for bit in HALF_STEP[::direction]:
                for _idx in range(4):
                    set_gpio(i2cdev,_idx, bit[_idx])
                time.sleep(0.1)
            _GPIO_VAL = 0
            write_reg(i2cdev, 0, bytes())


def main(i2cnum=7):
    with get_i2cdev(i2cnum) as i2cdev:
        _GPIO_VAL = 0
        step(i2cdev, 32)


if __name__ == '__main__':
    main()
