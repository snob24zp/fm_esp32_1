#!/bin/bash

python3 -m pip install -r src/requirments.txt
./fwupd.sh

exit $?
