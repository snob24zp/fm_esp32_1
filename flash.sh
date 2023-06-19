#!/bin/bash

# ampy -p $1 mkdir hw

if [ -z $1 ]; then
    echo "Usage $0 [port][board-file]"
    exit 1
fi

BOARD=$2
if [ -z $2 ]; then
    BOARD=esp32.json
fi

git submodule init
git submodule sync

SRCS=(.)

CMD="ampy -p $1"
# CMD="echo $1"
echo "Generate BSP"
rm src/board.py
jsonlint -Sf $BOARD | tools/json2py.py > src/board.py

for _lib in ${SRCS[@]}; do
    if [ $_lib != '.' ]; then
        $CMD rmdir $_lib &> /dev/null
        echo "Create dir $_lib"
        $CMD mkdir $_lib
    fi
    for _f in ./src/$_lib/*.py; do
        if [ $(basename $_f) == "setup.py" ]; then
            continue
        fi

        _rf="$_lib/$(basename $_f)"
        _mpy="./src/$_lib/$(basename $_f .py).mpy"
        mpy-cross $_f
        if [ -f $_mpy ] && [ $(basename $_f) != "main.py" ]; then
            _rmpy="$_lib/$(basename $_rf .py).mpy"
            echo "copying $_mpy -> $_rmpy"
            $CMD put $_mpy $_rmpy
            rm $_mpy
        else
            echo "copying $_f -> $_rf"
            $CMD put $_f $_rf
            if [ -f $_mpy ]; then
                rm $_mpy
            fi
        fi
    done
done


echo "Reset board"
$CMD reset
