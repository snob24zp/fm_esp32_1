# Topic /{hub}/info

Topic '/{hub}/info' sends by device as a next step (and final) steps of registration and contains current state of hub and connected to the hub devices

Example:

```
[1690137030] /48:3f:da:55:07:5b/info -> 
{
	"mac": "48:3f:da:55:07:5b",
	"version": "R230620;master;4588a7b7fbc59165f44ff9980aaf9df8077c9629",
	"type": "mpy",
	"prot": 2,
	"devices": [
		{"s": 3996365522, "t": 1, "r": {"0": 3996365522, "1": 1690137029}}
	]
}
```

Where 
* MAC - gives a hub identification (token)
* Version - Show current version of hub. Version contains a 3 part with ';' delimeter
	* First shows build which equals date and have format RYYMMDD
	* Second shows a used GIT-branch (here 'master' branch)
	* Latest is GIT commit
* Type - Simply type of hub (string and could be any)
* Prot - Protocol version. If missed then equals 1
* Devices - Devices state, in protocol version 1 it was a list with device serials which is connected to the hub
	* 's' - serial number of connected device
	* 't' -  Type of the device
	* 'r' - Current registers values. Register 0 always contains a serial number, and register 1 - registration time (in unixtime format)
