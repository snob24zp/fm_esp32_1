# Topic 'write'

Topic `write` - writes data inside device memory

Topic have next format: `[addr];[data-base64]` Where: `addr` - integer value of memory address, `data-base64` - Data to write encoded with base64
Response will have next format: `[addr];[size]` Where: `addr` - integer value of memory address, `size` - written size.

## Example

Writing memory:

```
>48:3f:da:55:07:5b/3996365522/write -> 32;NFY/669XnWvCNRMjVGYDVxYmVPBoOWyfWCY0Sjpt/6CvyX7QI+8STUTfLphYJDWqWBDwM5GtpAWF+ajHm+74Qw==
<48:3f:da:55:07:5b/3996365522/write -> "32;64"
```

