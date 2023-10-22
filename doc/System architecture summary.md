# System architecture

![[System architecture graph.png]]
## Parts of the system

* `Device` - User device, one user can have many devices, as well as one device could be controlled by many users (up to 32 users per device)
* `MQTT-Broker` - MQTT broker. In current implementation has been used Mosquitto, but mqtt-broker could be changes in any time, the main requirment support MQTT 3.1 version
* `Event storing server` - Microservice which listens generated events from devices and caching it. Which gives faster way to retrieve history of values changes to build plots, etc
* `FW Upgrade server` - Microservice which updates firmware on devices in automatic way. 
* `User server` - Microservice which provides device and user registration in the system and give more flexible way to manage devices by users
* `MQTT.JS Web application` - Web application which provides UI of the entire system and gives to user possibility controlling and managing own devices
* `User` - Physical user itself. Every user may have up to 32 devices

User controls device directly without any proxies between (except mqtt-broker)




