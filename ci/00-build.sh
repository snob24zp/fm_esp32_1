#!/bin/bash

python3 -m pip install --break-system-packages -r ./src/requirements.txt

ls -la src/
dotnet --version
./fwupd.sh

exit $?
