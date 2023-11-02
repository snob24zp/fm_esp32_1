#!/bin/bash

python3 -m pip install --break-system-packages -r src/requirments.txt
python3 -m pip install --break-system-packages demjson

./fwupd.sh

exit $?
