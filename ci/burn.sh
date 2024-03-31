#!/bin/bash

#echo "Press 'Reset' then 'Boot' buttons, after release 'Reset' button and after 'Boot' button"
#read
#sleep 3
./esputil -p /dev/ttyACM0 -b 460800 flash out/bins/AR.*.hex