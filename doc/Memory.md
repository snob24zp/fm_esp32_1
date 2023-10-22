# Memory Topics

## Brief 

Every device (client) should have a memory topics. Memory topics gives possibility to store some user data in device, and device can freely change this memory on the run. But unlike, registers, memory doesn't have a notification on each change, and could be read only by external command. Another difference with registers that there is only one linear memory space and user/device should map according to the usage. 

## Topics

There are only two topics inside: 

* `read` - Read device memory. Command have two parameters separated by `;`  - \[addr];\[size]. Response will have format - \[size];\[data]
* `write` - Write device memory. Format - \[addr];\[data] . Response will have format: - \[addr];\[size]

This topics uses base64 to encode the data
Check examples in [[Topic 'read']] and [[Topic 'write']]
