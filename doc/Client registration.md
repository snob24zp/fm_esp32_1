Client registration goes in a several steps:

1. Client sends his MAC address (ie HUB identification token, which could be not mac-address) to the public topic `/reg` ([topic reg](obsidian://open?vault=tasks&file=esp32-uclient%2Fmqtt-topics%2FTopic%20'reg'))
2. Server responds with a unixtime in mS to the topic `/{hub}/time`. This operation doing clock synchronization between server and client
3. Clients sends short information about devices, version, etc. See description of topic in [topic info](obsidian://open?vault=tasks&file=esp32-uclient%2Fmqtt-topics%2Fhub%2FTopic%20'info')
5. Hub, devices connected to the hub and server now in 'READY' state and can starts communications

Example:
```
[1690137029] /reg 48:3f:da:55:07:5b  
[1690137029] /48:3f:da:55:07:5b/time 1690137029023  
[1690137030] /48:3f:da:55:07:5b/info {"mac": "48:3f:da:55:07:5b", "version": "R230620;master;4588a7b7fbc59165f44ff9980aaf9df8077c9629", "type": "mpy", "prot": 2, "devices": [{"s": 3996365522, "t": 1, "r": {"0": 3996365522, "1": 1690137029}}]}
```

**All messages should be  JSON well-formed**

