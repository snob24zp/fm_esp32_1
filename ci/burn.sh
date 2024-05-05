#!/bin/bash

echo "Connect ESP-USB port (not CH340), then Press 'Reset' then 'Boot' buttons, after release 'Reset' button and after 'Boot' button"
read
sleep 3
./esputil -p /dev/ttyACM0 -b 460800 AR.*.hex