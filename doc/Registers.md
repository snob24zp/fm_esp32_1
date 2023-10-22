# Registers

Register - it's a basic data unit of the entire system, which can store, process, and signalize some basic information related to the device. For example, register '1', by default on all devices types, represents a time when was device has been established communication with server. So basically, 'Register' it's an 'endpoint' which represents some function in the device.

Another example, GPS tracker could have two registers with 'latitude' and 'longitude'. Or even one register, which calls a location.

Data in registers stores in JSON format. Name of register - simple number. 

Table of basic registers

| # register | Data type | Description | 
| --- | --- | -- |
| 0 | int | Represents a serial number of device| 
| 1 | int | Contains a device connection timestamp (when device has been pass registration on the server) |

Registers is event based system, on it's changes outside, device will generate a messages with a changed register state. 
To update register value from server side, server (or UI-client) sends a message to the register topic.

Register topic have next format: `{direction}{hub}/{device}/{reg}`
Example for protocol version 2:

```
[1690212391] >48:3f:da:55:07:5b/3996365522/8 16582
[1690212393] <48:3f:da:55:07:5b/3996365522/8 5623  
[1690212395] >48:3f:da:55:07:5b/3996365522/9 {"rnd-a": 55028, "rnd-b": 57214}  
[1690212397] <48:3f:da:55:07:5b/3996365522/9 {"rnd-a": 37600, "rnd-b": 13486}
```

Register value exchange, as a communication with other topics, have direction sign: 

* From server side to the device '>' (`>48:3f:da:55:07:5b/3996365522/8 16582`)
* From device to the server '<' (`<48:3f:da:55:07:5b/3996365522/8 5623`)

Protocol version 1, can exchange register values only as integer, and didn't have a direction character inside topic

```
[1690212395] /dc:a6:32:44:eb:fc/4832232/12 1115117322  
[1690212395] /dc:a6:32:44:eb:fc/4832232/6 47960  
[1690212395] /dc:a6:32:44:eb:fc/4832232/7 1105659259
```

[[Register topic]]

**All messages should be  JSON well-formed**

