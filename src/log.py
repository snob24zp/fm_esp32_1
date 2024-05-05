try:
    from time import ticks_ms
except ImportError:
    import time

    def ticks_ms():
        return int(time.time() * 1000)

import gc


class log:
    DEBUG = 3
    INFO = 2
    WARN = 1
    ERR = 0
    OFF = -1

    GLOBAL_LVL = DEBUG

    @staticmethod
    def set_log_lvl(lvl):
        log.GLOBAL_LVL = lvl

    def __init__(self, log_prefix: str = '') -> None:
        self.log_prefix = log_prefix

    def dbg(self, msg, *args, **kwargs):
        if log.GLOBAL_LVL >= log.DEBUG:
            # print(f'[{utime.ticks_ms():8d}]  [DBG] [{gc.mem_free()}] {self.log_prefix} ', msg, *args, **kwargs)
            print(f'[{ticks_ms():8d}]  [DBG] {self.log_prefix} ',
                  msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if log.GLOBAL_LVL >= log.INFO:
            print(f'[{ticks_ms():8d}] [INFO] {self.log_prefix} ',
                  msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        if log.GLOBAL_LVL >= log.WARN:
            print(f'[{ticks_ms():8d}] [WARN] {self.log_prefix} ',
                  msg, *args, **kwargs)

    def err(self, msg, *args, **kwargs):
        if log.GLOBAL_LVL >= log.ERR:
            print(f'[{ticks_ms():8d}]  [ERR] {self.log_prefix} ',
                  msg, *args, **kwargs)

    @staticmethod
    def dbg_wr(f):
        def wrapper(*args, **kwargs):
            args[0].dbg(f'enter {repr(f)} {args[1:]}')
            ret = f(*args, **kwargs)
            args[0].dbg(f'exit {repr(f)} ret: {ret}')
            return ret
        return wrapper
