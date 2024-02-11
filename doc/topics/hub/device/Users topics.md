# User topics

## 'user/add' topic

Adding user will be described in steps:

#### Step 1

To add user, need to have next information:

* `name` - Name of the user (ie phone)
* `global_permissions` - Flags with a global permissions to device functionality (like memory operations, user operations, etc)
* `uid` - User key, initial 32 byte field to sign the incoming/outgoing messages (HMAC/AES)
* `access_list` - List with a topics to which user have a permissions. 

#### Step 2

To encode data-string for user need to use next structure:

| Offset | Name | Description | 
| ---    | --- | --- |
| 0..31  | uid | User identification | 
| 32     | global_permission | Global permission (details check @ [[../../../Users\|Users]]) | 
| 33..97 | user_name | User name | 
| 97..*  | access_list | Array of 16 bits values with numbers of registers |

##### Example

User identificator: `fb81c4cc20a3d5d1c700b89c4ebaecf786ea76c0518c7592119b6949f912d44e`
Global permission byte:`ff`
Username: admin@admin.com -> `61646d696e4061646d696e2e636f6d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000`
Access list: 3,4,5,6,7,8,12,32,1024 -> `000300040005000600070008000c00200400`
Entire packet in hex view: `fb81c4cc20a3d5d1c700b89c4ebaecf786ea76c0518c7592119b6949f912d44eff61646d696e4061646d696e2e636f6d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000300040005000600070008000c00200400`
Base64 encoded packet: `+4HEzCCj1dHHALicTrrs94bqdsBRjHWSEZtpSfkS1E7/YWRtaW5AYWRtaW4uY29tAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAQABQAGAAcACAAMACAEAA==`

#### Step 3

Encrypt and sign the packet via AES128-CBC-SHA256-HMAC.

on python such operation will be looks like:

```Python
def encrypt(data: bytes, shared_key: bytes, hmac_key: bytes, iv_bytes: bytes = bytes(16 * [0])):
"""encrypt data with AES-CBC and sign it with HMAC-SHA256"""
	pad = AES.block_size - len(data) % AES.block_size
	data += bytes(pad * [pad])
	cypher = AES.new(shared_key, AES.MODE_CBC, iv_bytes)
	encrypted_data = cypher.encrypt(data)
	sig = hmac.new(hmac_key, encrypted_data, HASH_ALGO).digest()
	return (encrypted_data, sig)
```

Where:
* IV is set to 0 (ie `[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]`) by default or could be set to another value via appropriate register
* shared key is set to even bytes from hmac_key (every second `UID[::2]`)
* hmac_key - UID/DID. **In case when device don't have users inside - as UID should be used DID**

Result with message above will be looks like:

```
dpi77PvhyGtdpQGiV/rBtPMwtEtgTz2j/6+E73Mw2/yYslvifMZL6hxMr9zxmZy//dOG5RXecTvQmrzwlPlePu+Uc8JJlOQ7p8fgOSG6V2Eg1X+xZInP/3Fkyyp06P1knPwlVI0/INRK9AHVAHShiBQl/nOtzD34kSo8U2nCV6g=.cF6xf8/xRysOLWEMeTCwjWP0CyUV0N1mmiUimjOJ7As=
```

#### Step 4

This encoded message should be sent to the `>{mac}/{serial}/user/add` topic. As return value, device should send user number.

## 'user/list' topic

To invoke list, ciphered message `list` should be sent to the `>{mac}/{serial}/user/list` 
In return will be provided a list with username and permissions list.

Returned list will consist from a user count messages. Ie 1-user - 1message. The last message will be with empty json object. Which shows there are no more users to list
Format of incoming message will be: 

| key | type | Description |
| --- | --- | --- |
| 'u' | base64 - 32 bytes | User Identification |
| 'n' | str - up to 64 bytes | User name |
| 'p' | uint8_t | Global permissions |
| 'a' | array of uint16 | Access list |

Incoming message should be signed and encrypted with user key. Outgoing (from device) message will be signed with device identificator and encrypted with a requester user key


Example:
```
[1697650141] >48:3f:da:55:07:5b/3996365522/user/list "0SkB9NvLAGW3K4TfL+RFCQ==.yRV/XHc1AkRI6e9AZXaVSpWu1hGpbS54q6YuGDSGjOQ="  
[1697650142] <48:3f:da:55:07:5b/3996365522/user/list "sPx+zoGX8Q4BZg8zJqGB9ZPDGVPk7bXQq07KDSeuzAg97BZSOy0uG/Uxwl/5PnkrQUYwKG4zRfKietuZmkWZ7UiIvwCqlQycVX9kX9m0ePZaoS8qSN+zHpdirrWM6NQEkN8BRNdaWy9EUF4fU4k3Hw==.1e45xHnflC8aSj//Vb54gdroCYn8PtUuZgpM  
oxZ/npY="  
...
[1697650142] <48:3f:da:55:07:5b/3996365522/user/list "OZAHf/qHwrjqyz/sBkXpdo/DPMqpdVxaQFHU8DHru0Tf2ZazlLLvlZKrFzdFfGO+KnSMNUU6aAcgy5nDF7Payxqu49wz+4guxvPkj2Yg5fxQSGZOMYuaHIa5bVcY8Tvkkmv2Ouhr/2JkEHsRSe2C8A==.KAKopNMMfgFn8/32qgr0HbgP2s+GTlrO+rH0  
6Q7Hc6c="  
[1697650142] <48:3f:da:55:07:5b/3996365522/user/list "VzARoMqwi4vQBcbdYv1TfO7w0FHCad2IQy8YmMjOnze6+bkqrIrgLggny9ENcXOT85KMHRuvB6joTjlRkq84eExlckXRUI8fW5VLMXlg5HvEa++/f3zrnvWSRs9aUoYnQ9Gwx3ROqskuxDbgZ7CTWw==.Lco8bt4iZ+P6y5oytTyvnlct7dtIwQjps9Kj  
MD3SWLg="  
[1697650142] <48:3f:da:55:07:5b/3996365522/user/list "zFLMbCkKQB75ADPKvWfg4g==.a/liPaIc69QWc0ZDU+vEf8f0RTwtJLbO9Q2HFxdJ0hA="
```

When it will be decrypt, that will be looks like:

```
[1697650142] >48:3f:da:55:07:5b/3996365522/user/list list
2023-10-18 19:29:02,056 - TEST - INFO - list response: (user/list) {'u': '+4HEzCCj1dHHALicTrrs94bqdsBRjHWSEZtpSfkS1E4=', 'n': 'admin@admin.com', 'p': 255, 'a': [-1]}
...
2023-10-18 19:29:02,188 - TEST - INFO - list response: (user/list) {'u': 'z2C9HjZpnMJ8OmWA7pRvXqEU/3uAYzamELErc14cn6c=', 'n': 'amiable.linda@outlook.com', 'p': 255, 'a': [-1]}
2023-10-18 19:29:02,191 - TEST - INFO - list response: (user/list) {'u': 'yhOkYrJWU/98dOn4+IwvfBUUHf9O9LvGt+g1Z/NEvHc=', 'n': 'charming.james@dlab.pw', 'p': 255, 'a': [-1]}
2023-10-18 19:29:02,209 - TEST - INFO - list response: (user/list) {}
```

## 'user/remove' topic

To remove user, need to send every odd byte from UID in a ciphered way to the `>{mac}/{serial}/user/remove`

Example:
```
[1698916251] >48:3f:da:55:07:5b/3996365522/user/remove "+GvyJqRVblo8nah11stQ0ohHGW5uJnw2Kx/h7GjTCyvgqah/MX75LPShbgvXi+/F.+pgnFZICjAW+Rc61TXIkODAEpP5IOS4SQSvJWD0c+ZU="  
[1698916252] <48:3f:da:55:07:5b/3996365522/user/remove "LY4YVzC3waUcqthcsYyA6A==.qOn6Czfan1IbrJmfXjdBHXmv4Qr1zMEhFuMrfWrEVng="
```

Where input is - encrypted user-id, and output will be encrypted string 'OK'. 
Encryption and decryption goes in the same way as in `user/list` or `user/add`
## '>user/dev' Global topic

This topic is used to search devices which belongs to user. To use it, in this topic should be sent sha256 hash of UID. All devices which have this user will answers with their MAC

example:

```
[1698916319] >48:3f:da:55:07:5b/3996365522/user/add "J8GTl7SsleUnuPB7dDFeuC8H9p0DqRakOESA2TMzPdt87U7HJ6xID8J+Pl1Yor/PRyw5Sg9xDF9ssU76TnMeSdU6CAUEj513Bn7xmNXaPaW9fd+mhgp2UthablkMIRPr7QGz0Lw+YXRLzpJmVpisNg==.6KMI62AT1YzWAQ4SWOxESxwfDhoAm1+JBIBvU  
Qsvuco="  
[1698916319] <48:3f:da:55:07:5b/3996365522/user/add "hdMU2nT5by40zEY21b1Ufg==.F1SYOOcOwzmUSeNJDfOJjHHt6JMjw/o3mwEREqPbwWE="
----
[1698916320] >user/dev yt2q8P3UwdnRsQHRD9VS9TKrGx0aaSfbDOXC7m1xjHY=  
[1698916320] <user/dev 48:3f:da:55:07:5b/3996365522
```

