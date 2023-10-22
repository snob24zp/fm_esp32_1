---
gists:
  - id: daf7bd020abcda4c8edc686e4210ef36
    url: 'https://gist.github.com/intx82/daf7bd020abcda4c8edc686e4210ef36'
    createdAt: '2023-07-22T10:44:54Z'
    updatedAt: '2023-07-22T10:44:55Z'
    filename: Hardware and firmware summary.md
    isPublic: true
---

## Requirements

Hardware and firmware part of the device must meet next requirements:

* Have connectivity to the internet via WI-FI 
* Have connectivity to the customer mobile device (tablet/phone) via Bluetooth
* Have connectivity to the internet via mobile network (2G/3G/4G/5G)
* The data which will be collected from sensors must be stored in the device and on the remote server (Cloud service)
* Device and entire system must send SMS if some dangerous condition found
* Have a firmware upgrade from the server (FOTA, firmware over-the-air upgrarde)

## Selecting hardware parts

### WI-FI, Bluetooth connectivity

To implement 'Farm monitor' device has been selected ESP32-WROOM-32D MCU (main control unit). 

ESP32-WROOM-32D is a modern MCU which have next connectivity interfaces:

* WI-FI 
* Bluetooth

Both interfaces are working on the same frequency (2.4 GHz) and can work simultaneously using only one antenna 
On the current version of designed PCB used the same MCU, so this part of the board could be the same

### Mobile broadband connectivity

To have a mobile connectivity on a current board has been used SIM800D modem. This is a good choice, but the main disadvantage of this modem is missed support of modern networks like LTE. We can use it successfully, but preferred to use his successor A7630 or A7670.

### Storage

ESP32 MCU have support external flash-memory up to 16 mbytes, which will be used as main storage device. The second option is to use SD-Card as primary storage. Both storages could be used simultaneously 

### Summary hardware

If take into account all selected parts and given requirements, on the market already available designed PCB. Could be nice to use it and didn't develop anything new.
This board has a name LILYGO T-A7670E/G/SA R2 [https://www.lilygo.cc/products/t-sim-a7670e]

As bonus this board has support GPS (which is not needed in this project)

## Firmware

Firmware will be use next protocols to communicate with a cloud:

* MQTT
* SMS

SMS or WI-FI or Bluetooth will be used as initial configuration service. 

Due to sensors measured with static intervals, the system will be event-based. This means after each measurement, the entire system will send 'event' to the server and store it into internal memory. If there are any power or connectivity issues happens, the device will store result of measure into the internal storage and when connectivity will be again available will send it to the server. 

### Initial configuration procedures

Device which is connected via mobile network will be already available on the cloud, and don't need any initial configuration.
On other hand, device which use WI-FI needs to be configured first, and this will be done via WI-FI access point (captive portal) or Bluetooth

