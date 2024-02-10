# Getting Started

## 0. Requirments

To follow this instruction you should have:

* ESP32 device kit (ESP32-devkit-v1)
* Linux PC (you may use RPi or other device which runs ubuntu/debian linux)

## 1. Burning micropython into the ESP32 board

More details related to micropython could be found at [https://docs.micropython.org/en/latest/esp32/tutorial/intro.html](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)

1. To burn micropython into ESP32 you should download esp-tool. Tool could be found here: https://github.com/espressif/esptool/ or downloaded via `python -m pip install esptool`
2. Connect board to the PC
3. With esp-tool erase current contents of flash `esptool.py --port /dev/ttyUSB0 erase_flash` (Note: port could be different)
4. Go to official micropython esp32 port page and download latest Micropython firmware: https://micropython.org/download/ESP32_GENERIC/
5. Write downloaded firmware into ESP32 Flash: `esptool esp32c3 -p /dev/ttyUSB0 -b 460800 --before=default_reset --after=hard_reset --no-stub write_flash --flash_mode dio --flash_freq 80m --flash_size 4MB 0x0 bootloader.bin 0x10000 micropython.bin 0x8000 partition-table.bin`
6. Open any Serial terminal with provided port above (`/dev/ttyUSB0`) and speed 115200, and press enter, you should see prompt `>>>`

## 2. Uploading firmware 

1. Install `ampy` tool and `GitPython` library. (`python3 -m pip install adafruit-ampy` and `python3 -m pip install GitPython` )
2. Start `./flash.sh /dev/ttyUSB0`
3. After you may open terminal and watch logs:

```logs
[   11481] [INFO] FW-UPD  Initialized  
[   11506] [INFO] WEBAPP  init done
```

If you see it, then device ready to work

## 3. Initial configuration

Now device ready to work. To configure network, you need connect to device Wi-Fi access point (will looks like `AR-[12 digits and letters]`) and go to the http://192.168.4.1.
After a while, when device stops scanning Wi-Fi networks select yours, write the password of this network and press button `Connect`. Now you should have device connected to the yours Wi-Fi. 

## 4. Simulator start

To check protocol and other stuff, firmware could be started as python application itself:
```bash
$python3 src/main.py
```

Device web page will be available at port 3000 (http://localhost:3000)

## 5. UART Bridge application

@see [[Example app - UART bridge]]
