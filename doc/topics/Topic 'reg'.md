# Topic '/reg'

Topic reg start a client registration on the server. It's an entry point on server which listens for connected hubs 'token'. On start hub registration on the server, hub must send to this global topic his token, as response server should sends to topic `/{hub}/time` - unixtime in mS

Hubs token mostly is MAC address, but could be any other string which correctly identifies a hub.

Example:

```
[1690137029] /reg 48:3f:da:55:07:5b  
[1690137029] /48:3f:da:55:07:5b/time 1690137029023
```

Direction of topic:  HUB -> SERVER

More details about registration could be found in [client registration](obsidian://open?vault=tasks&file=esp32-uclient%2FClient%20registration)

