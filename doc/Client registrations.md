# Client registrations

## Registration

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

## Deregistration

If device lost unexpectedly connection, MQTT broker via 'Last-Will-Testament' will publish message to the status topic with `-1` value

Example:

```
[1699479753] /reg 48:3f:da:55:07:5b  
[1699479753] /48:3f:da:55:07:5b/time 1699479753481  
[1699479754] /48:3f:da:55:07:5b/info {"mac": "48:3f:da:55:07:5b", "version": "R231102;master;e9b306c7e765ddf633df5089542fbb0d0e965da4", "type": "mpy", "prot": 2, "devices": [{"s": 3996365522, "t": 1, "r": {"0": 3996365522, "1": 1699479753}}]}  

------ unexpectedly lost the connection ----

[1699479755] <48:3f:da:55:07:5b/status -1
```

