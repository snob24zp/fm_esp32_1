# Example app - UART bridge

## Message format

Simulated device will use third register (`[><][mac]/[serial]/3`) as pipe channel, so any publishing into this register will lead transmitting this data into TTY, and vice-versa.
Any data received in TTY will be forwarded to this register. Internally TTY have 10ms as maximum interval between symbols, on timeout - message will be transmitted into mqtt. 

## Linux

Under linux os, application will try to create a PTY pipe (`/tmp/uart`) . That pipe could be opened with any terminal, for example `tio` or `miniterm` on any available speed

Example:
```bash
$ python3 -m serial.tools.miniterm /tmp/uart  
--- Miniterm on /tmp/uart  9600,8,N,1 ---  
--- Quit: Ctrl+] | Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---  
"hello mqtt"
```

## Micropython (ESP32)

---

## Windows

---
