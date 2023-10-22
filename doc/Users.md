# Users

## Brief

Users functionality gives ability to control permissions and access to dedicated functionality / topics. 

All  topics could have a 3 security variants:

* None - Topic could be written by anyone, ie public access
* HMAC - Incoming/Outgoing message should be signed to provide authentication of user
* AES-HMAC - Fully encrypted incoming/outgoing message, with additional HMAC

There are two types of identifications stores in device. One identification per user, and one global identification of device. 
* `Device identificator (did)` - will be generated from a WIFI name and WIFI password via sha256 hash function if has been used WIFI connection. Or through the same sha256 from number of phone if has been used connection via mobile broadband. 
* `User identificator (uid)` - Which is adds on creating user in the device and should be generated via sha256 from a username and password

Information related to used topics could be found in [[Users topics]]

## User data

User described by next information: 

* `name` - Name of the user (ie phone)
* `global_permissions` - Flags with a global permissions to device functionality (like memory operations, user operations, etc)
* `uid` - User key, initial 32 byte field to sign the incoming/outgoing messages (HMAC/AES)
* `access_list` - List with a topics to which user have a permissions. 

Access list item itself have a number of register in which user can write
 * Number of topic (16 bit) 

**Device could store only 32 users.** (see user_device.MAX_USER_CNT)

User identificator is not checked to validity, only on presence. UID should be generated from:
```Python
sha256(user_name + "\0"  + password)
```
#### Example:

* Username: `admin@admin.com`
* Password: `11223344`
* Text before hashing:  `admin@admin.com\011223344`
* Text before hashing in hex view: `61646d696e4061646d696e2e636f6d003131323233333434`
* UID in hex view: `fb81c4cc20a3d5d1c700b89c4ebaecf786ea76c0518c7592119b6949f912d44e`
* UID in base64: `+4HEzCCj1dHHALicTrrs94bqdsBRjHWSEZtpSfkS1E4=`

#### Global permissions:

| Bit | Name | Description |
| --- | --------- | -------------------------- |
| 0 | rfu | - |
| 1 | write | Allow user to globally write into registers |
| 2 | mem_read | Allow user read memory from device |
| 3 | mem_write | Allow user write memory from device |
| 4 | fw | Allow firmware upgrade |
| 5 | events | Allow to user read events from device |
| 6 | users | Allow to user control another users |
| 7 | root | Allow user do factory reset of the device |

Where 0xff - allow everything (ie superuser), and 2 - normal user which could only control some points

## Signing messages

Signing message in going via HMAC function (RFC2104) ([https://en.wikipedia.org/wiki/HMAC](https://en.wikipedia.org/wiki/HMAC))

Outgoing message from device is signed by `device identifactor`. Incoming should be signed via `user identificator`
Signed message will have next format: 

| Data | Divider | Sign |
| --- | --- | --- |
| 1103560704 | . | /xQfpY7TUQo+1QcNaJopuaXytCClf7HTKcDta9lKDNc= |

Signed signature is provided in base64 format.

#### Example:
  
| Query | Topic | Data |
| -------------------- | --------------------------------- | --------------------------------------------------------------------------------------------- |
| Writing data into 3-rd register | /aa:bb:cc:dd:ee:ff/11223344/3 | "1103560704./xQfpY7TUQo+1QcNaJopuaXytCClf7HTKcDta9lKDNc=" |
| Writing memory | /aa:bb:cc:dd:ee:ff/11223344/write | "512;ggXLmX3EMFCVa5NTud4AL4L0R+ts3vC0JypOAhbOTYw=.NbTV9IEf1YQNebx7lrteRs8fr23NRsve/QcUVTo446g=" |

