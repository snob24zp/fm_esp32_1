# Firmware update

## Summary 

Firmware update could be divided into three variants of updating:
* Updating via http web page located on the device
* Updating via mqtt firmware update topics, where server push the data to the device (in-band - means inside-mqtt)
* Updating via mqtt firmware update topics, where device downloads itself remote package (out-of-band - means outside-mqtt)

More information about firmware package structure could be found in [[UEBA bootloader]] and in [[Device filesystem]]]
## Updating via device web page

Every device have a internal web-server to make initial configuration of system. This web-server also have a page (http://[device-ip]/fw.html) which gives possibility to update the firmware in device.

To update firmware internal web-server uses two API endpoints:

* `/fw_upd` - Controls the internal state of firmware update
* `/fw_pkg` - For transferring firmware data chunks

Where `/fw_upd` can receive only 4 commands which represents (equals) of the internal state firmware update finite state machine

| Command/State | Description | 
| ---- | ---- |
| 0    | Resets the firmware update finite state machine to initial state |
| 1 | Command which starts uploading firmware chunks |
| 2 | Verification command/state. On this step device tries to mount received decrypted disk image, if error happens will be returned 'error' |
| 3 | Reboot and start copying files (updating) from mounted disk image to root partition |

`/fw_pkg` receives only raw chunk data (for AR device 512 byte). To this query will be returned a number of next chunk, or an error. Return have JSON object format: 

```
<-- ur+pvhIKUSECbFeXm7z4URHbIss3f+...
--> {"chunk", 118}
```

Example:
	1. Send `1` to `/fw_upd`, and wait to `OK` - That's initialize firmware update stack
	2. Sends chunks from firmware file as is (ie in base64 encoding) into `/fw_pkg`, will be returned a number of next chunk (ie 0,1,2,3, ---, 3, 4, 5 ). In case of network issues, updater may send the same chunk again and waits for the number of next chunk in answer.  (`"ur9j2VWzouKn08iVE..." > /fw_pkg`)
	3. Send `2` to `/fw_upd` to check the uploaded image and wait for answer `OK`
	4. Send `3` to `/fw_upd` to update the entire system, there will not be any answer

![[Pasted image 20231028154734.png]]
...
![[Pasted image 20231028154840.png]]

## In-band MQTT firmware update

In-band MQTT firmware upgrade works in the same way as HTTP upgrade, but in this case endpoint is located in MQTT (as device topics)

Example:

```
[1698504465] >48:3f:da:55:07:5b/3996365522/fw_upd 1  
[1698504465] <48:3f:da:55:07:5b/3996365522/fw_upd "OK"  
[1698504466] >48:3f:da:55:07:5b/3996365522/fw_pkg "ur9j2VWzouKn08..."  
[1698504466] <48:3f:da:55:07:5b/3996365522/fw_pkg {"chunk": 1}  
[1698504467] >48:3f:da:55:07:5b/3996365522/fw_pkg "ur9IYXFXOd..."  
[1698504467] <48:3f:da:55:07:5b/3996365522/fw_pkg {"chunk": 2}  
[1698504468] >48:3f:da:55:07:5b/3996365522/fw_pkg "ur84aI..."  
[1698504469] <48:3f:da:55:07:5b/3996365522/fw_pkg {"chunk": 3}  
...
[1698504758] <48:3f:da:55:07:5b/3996365522/fw_pkg {"chunk": 226}  
[1698504759] >48:3f:da:55:07:5b/3996365522/fw_pkg "ur8XdhLeWlvZgTI0..."  
[1698504759] <48:3f:da:55:07:5b/3996365522/fw_pkg {"chunk": 227}  
[1698504760] >48:3f:da:55:07:5b/3996365522/fw_pkg "ur833l/xdx2/zr4UtRNY0JNk..."  
[1698504760] <48:3f:da:55:07:5b/3996365522/fw_pkg {"chunk": 228}  
[1698504761] >48:3f:da:55:07:5b/3996365522/fw_pkg "ur/OC8Gk1mZYJH0M3KRL.."  
[1698504761] /48:3f:da:55:07:5b/status 229  
[1698504761] <48:3f:da:55:07:5b/3996365522/status 229  
[1698504761] /48:3f:da:55:07:5b/error 1  
[1698504761] <48:3f:da:55:07:5b/3996365522/fw_pkg {"chunk": 229}  
[1698504763] >48:3f:da:55:07:5b/3996365522/fw_upd 2  
[1698504764] <48:3f:da:55:07:5b/3996365522/fw_upd "OK"  
[1698504765] >48:3f:da:55:07:5b/3996365522/fw_upd 3  
[1698504765] <48:3f:da:55:07:5b/3996365522/fw_upd "OK"
```

@see [[topics/hub/device/Firmware update topics|Firmware update topics]]

## Firmware update via out-of-band download

The main difference with in-band uploading, that there device itself downloads file from the server. For such purpose there added topic `fw_url`

Algo:

1. Server sends url to `fw_url` topic
2. Device downloads it, while it downloads, device sent total downloaded size, on done device will send word `OK`
3. Send `2` to `/fw_upd` to check the uploaded image and wait for answer `OK`
4. Send `3` to `/fw_upd` to update the entire system, there will not be any answer

Example:

```
[1698835346] >48:3f:da:55:07:5b/3996365522/fw_url "https://release.dlab.pw/AR.FW.latest.uebf"  
[1698835347] <48:3f:da:55:07:5b/3996365522/fw_url 512  
[1698835347] <48:3f:da:55:07:5b/3996365522/fw_url 1024  
[1698835347] <48:3f:da:55:07:5b/3996365522/fw_url 1536
...
[1698835357] <48:3f:da:55:07:5b/3996365522/fw_url 174080  
[1698835357] <48:3f:da:55:07:5b/3996365522/fw_url 174592  
[1698835357] <48:3f:da:55:07:5b/3996365522/fw_url 174848  
[1698835364] <48:3f:da:55:07:5b/3996365522/fw_url "OK"
[1698835366] >48:3f:da:55:07:5b/3996365522/fw_upd 2  
[1698835367] <48:3f:da:55:07:5b/3996365522/fw_upd "OK"  
[1698835368] >48:3f:da:55:07:5b/3996365522/fw_upd 3  
[1698835368] <48:3f:da:55:07:5b/3996365522/fw_upd "OK"
```

**OUT-OF-BAND Downloading forbidden if device don't have file `data/fwupd.hosts` and this file doesn't contains first part of the URL**

Example of contents of the `data/fwupd.hosts` file:

```
http://releases.dlab.pw/
http://x.ks.ua/
```

That's shows that firmware file could be downloaded only from this sites which starts with this part of url. i.e -> http://releases.dlab.pw/ar-device/AR.FW.latest.uebf will be allowed, but http://dlab.pw/AR.FW.latest.uebf not

