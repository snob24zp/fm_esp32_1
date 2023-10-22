Device should have a time series database inside. This 'Time DB' inside designed to fill the gaps when there is no connection to the network (server)
History consists of events. Event - key-value pair, where key is unixtime and value - value of register changed in this time. 

To retrieve events device have a one topic, `events/{reg}`. Details could be found [[Events topic]]
