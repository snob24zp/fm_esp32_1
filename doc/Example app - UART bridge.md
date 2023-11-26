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

## Micropython (ESP32-C3)

Device based on ESP32 will use UART0 as default uart device, RX and TX pins will be mapped to 20 and 21 pin respectively. This configuration could be changed in `esp32.json` board definition file. UART is using 115200 8N1 configuration. 

REPL, in the same time, will be available at internal USB Serial port (details: https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-guides/usb-serial-jtag-console.html)

Also, to use such configuration, Micropython build set MICROPY_HW_ENABLE_UART_REPL to zero. Check `ports/esp32/boards/ESP32_GENERIC_C3/mpconfigboard.h`

Already built Micropython release with these changes could be found in `other/esp32-c3_wo_repl` folder, and could be 'burned' by `deploy.sh` script (needed esptool.py)

#### Device related registers

On real device, except 3-rd register also available, registers 3,4,5,6. Where:

* Register 3 - UART Pipe, which silently transfers data from MQTT to BLE and to UART, and vice-versa
* Register 4 - Color of internal LED on [ ESP32-C3-DevKitM-1](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/hw-reference/esp32c3/user-guide-devkitm-1.html) 
	* Used RGB integer format, ie to set red diode color - need to write 16711680 value (converted from hex - 0xff0000)
* Register 5 - Used to send SMS, and due to current limitation will work only via wifi connection, but with presence SIM-card. To force connection to wifi option use register 6 
	* Used JSON format: `{"to":"+3812345678", "msg": "Message which should be sent"}`
* Register 6 - Used to force WIFI connection, if set this register to 1, device will reboot and try to establish a connection via WIFI instead of GSM/LTE. To set default value, write into it - 0

## Windows


