# Topic 'lifetime'

Topic 'lifetime' responsible about time between publishing statuses

```plantuml
@startuml
skinparam backgroundcolor transparent
skinparam monochrome reverse


entity Device as device
entity Server as server

device -> server: Send status with current count of transmitted messages since connection
device -> server: Device send some message to the server
server -> device: Server send some message to the device
device -> device: Wait 'lifetime' interval
device -> server: send status with count of transmitted messages
@enduml
```

By default lifetime is set to 60 sec

Example:

```
[1698845947] <48:3f:da:55:07:5b/3996365522/status 0
...30 messages
[1698846007] <48:3f:da:55:07:5b/3996365522/status 30
[1698846008] >48:3f:da:55:07:5b/lifetime 120
[1698846127] <48:3f:da:55:07:5b/3996365522/status 30 
```