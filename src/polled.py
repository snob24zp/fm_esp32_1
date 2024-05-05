"""
Polling class (aka scheduller)
"""
import time

try:
    from time import ticks_ms
except ImportError:
    def ticks_ms():
        return int(time.time() * 1000)
    time.ticks_ms = ticks_ms



class polled:
    """
    Polling class (aka scheduller)
    """
    def __init__(self, interval=100, args=(), kwargs={}):
        self.__call_intval = interval
        self.__pre_call_tm = 0
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        if self.__call_intval == 0 or time.ticks_ms() >= (self.__pre_call_tm + self.__call_intval):
            self.__pre_call_tm = time.ticks_ms()
            self.poll()

    def poll(self):
        pass

    @staticmethod
    def schedule(tasks):
        for task in tasks:
            if callable(task):
                task()
