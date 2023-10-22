# Events topic

Events topic has next topic format: `{direction}{hub}/{device}/events/{reg}` . Where `reg` - register number from which will be read stored events (about other parts refer to [[Registers]])

Request format: `[unixtime from];[unixtime to]`
Response format - JSON arrays per message, the last one will be empty JSON object. Inside JSON object: `tm` - Event unixtime. `r` - Register number `v` - Register value on this moment. 

## Example

```
>48:3f:da:55:07:5b/3996365522/events/9 -> 1690733325857;1690733401009  

<48:3f:da:55:07:5b/3996365522/events/9 -> [{"ts": 1690733239732, "r": 9, "v": {"tm": 1690733239732, "rnd_a": 1061528122, "rnd_data": "MLuXZrk="}}, {"ts": 1690733244751, "r": 9, "v": {"tm": 1690733244750, "rnd_a": 963492364, "rnd_data": "/heSWqGPqrIWqONDHPCD2Z8="}}, {"ts": 1690733249764, "r": 9, "v": {"tm": 1690733249764, "rnd_a": 1046598700, "rnd_data": "CBI752NuFRsLzf6lDD7U"}}, {"ts": 1690733330859, "r": 9, "v": {"tm": 1690733330857, "rnd_a": 367334316, "rnd_data": "Zpo7f6PoxkFuGXe+GMY3idW/Wiil2dNtUSA="}}]  

<48:3f:da:55:07:5b/3996365522/events/9 -> [{"ts": 1690733335863, "r": 9, "v": {"tm": 1690733335862, "rnd_a": 785519834, "rnd_data": ""}}, {"ts": 1690733340870, "r": 9, "v": {"tm": 1690733340869, "rnd_a": 1065557801, "rnd_data": "fQK757pXSjVXgz72ee047o4qzg=="}}, {"ts": 1690733345892, "r": 9, "v": {"tm": 1690733345891, "rnd_a": 462968454,"rnd_data": "N3dNOcb1l26lBjnR2pkaMTO87aZcjTycp7vLchU="}}, {"ts": 1690733350899, "r": 9, "v": {"tm": 1690733350898, "rnd_a": 224331738, "rnd_data": "g5A="}}]  

<48:3f:da:55:07:5b/3996365522/events/9 -> [{"ts": 1690733355907, "r": 9, "v": {"tm": 1690733355906, "rnd_a": 759950597, "rnd_data": "V7LYfYN0k6r+XbVH1DknnUaM32C55Qv+TcbAtmuR"}}, {"ts": 1690733360919, "r": 9, "v": {"tm": 1690733360914, "rnd_a": 272898953, "rnd_data": "FOOU4Qv5hnZ9WxVZcg=="}}, {"ts": 1690733365920, "r": 9, "v": {"tm": 1690733365919, "rnd_a": 622960054, "rnd_data": "qgK6IjwWV45VngfPefLst+5Bb0DxwtQv/etdJ9fi4Cw="}}, {"ts": 1690733370927, "r": 9, "v": {"tm": 1690733370925, "rnd_a": 98654007, "rnd_data": "aGlW73b7VWfJ"}}]  

<48:3f:da:55:07:5b/3996365522/events/9 -> [{"ts": 1690733375929, "r": 9, "v": {"tm": 1690733375928, "rnd_a": 642962425, "rnd_data": "hBz1QSF0nDSMoCQ="}}, {"ts": 1690733380942, "r": 9, "v": {"tm": 1690733380940, "rnd_a": 673199520, "r  
nd_data": "TT/jyH3ySIYcOxq2Oy+0ey9XbulfVVA="}}, {"ts": 1690733385956, "r": 9, "v": {"tm": 1690733385955, "rnd_a": 292488225, "rnd_data": "6+OuTB0YpnUWXw=="}}, {"ts": 1690733390958, "r": 9, "v": {"tm": 1690733390957, "rnd_a": 488017318, "rnd_data": "R2mk"}}]  

<48:3f:da:55:07:5b/3996365522/events/9 -> [{"ts": 1690733395987, "r": 9, "v": {"tm": 1690733395979, "rnd_a": 227258940, "rnd_data": "x+5FuGKXzQwuk6MbxHE="}}, {"ts": 1690733400992, "r": 9, "v": {"tm": 1690733400991, "rnd_a": 939626847  
, "rnd_data": ""}}]  

<48:3f:da:55:07:5b/3996365522/events/9 -> {}
```

