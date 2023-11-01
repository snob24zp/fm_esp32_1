import sys

if sys.version.count('MicroPython') > 0:
    import _thread 
else:
    import threading

def start_thread(cb, args):
    if sys.version.count('MicroPython') > 0:
        _thread.stack_size(10*1024)
        _thread.start_new_thread(cb, args)
    else:
        _th = threading.Thread(target=cb, name=f"{cb.__name__}-thread", daemon=True, args=args)
        _th.start()


