#!/bin/bash

python3 -m pip install --break-system-packages -r ./src/requirements.txt
sudo apt install -y python3-demjson

ls -la src/

./fwupd.sh

exit $?
