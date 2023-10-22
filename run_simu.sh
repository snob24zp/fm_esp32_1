#!/bin/bash

BOARD=$1
if [ -z $1 ]; then
    BOARD=linux.json
fi

echo "Generate BSP"
rm src/board.py
jsonlint -Sf $BOARD | tools/json2py.py > src/board.py

python3 src/main.py