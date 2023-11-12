import sys

if sys.version.count('MicroPython') > 0:
    import _thread 
else:
    import threading

def start_thread(cb, args, thread_stack = 12288):
    if sys.version.count('MicroPython') > 0:
        _thread.stack_size(thread_stack)
        _thread.start_new_thread(cb, args)
    else:
        _th = threading.Thread(target=cb, name=f"{cb.__name__}-thread", daemon=True, args=args)
        _th.start()


