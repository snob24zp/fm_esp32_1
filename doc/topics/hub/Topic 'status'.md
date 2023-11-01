# Topic status

Topic status shows total count of sent messages since connection to the server. This topic used as marker of missed messages. For example if some message will be miss in the middle in transmission, clients add this counter, while server not, then server can start registration again and retrieve missed value.

@see [[Topic 'error']]

Example:

```
[1698845947] <48:3f:da:55:07:5b/3996365522/status 0  
[1698845948] <48:3f:da:55:07:5b/3996365522/8 0  
... 28 messages  
[1698845980] <48:3f:da:55:07:5b/3996365522/8 29   
[1698846007] /48:3f:da:55:07:5b/status 30  
[1698846007] <48:3f:da:55:07:5b/3996365522/status 30
```

