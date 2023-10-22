# Topic Read

Topic `read` -  reads memory from device

Topic have next format: `[addr];[size]` Where: `addr` - integer value of memory address, `size` - Size which should read from device
Response will have next format: `[size];[data-base64]` Where `size` - read size, `data-base64` - Read data encoded with base64

## Example

Reading memory:

```
>48:3f:da:55:07:5b/3996365522/read -> 32;64 
<48:3f:da:55:07:5b/3996365522/read -> "64;unGdeR87c7HfzQ0c/sRhDoIvINqlmwFNp4fxZXsFJz6RZp6bYG9OiZR/toIVVE5De/SeMIVrnbsAUwMsvm7pJA=="
```
