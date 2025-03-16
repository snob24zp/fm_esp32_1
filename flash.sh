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

SRCS=(hw "hw/${BOARD%.*}" net uclient .)
HTMLS=(static)

CMD="ampy -p $1"
MPY_CROSS="./tools/mpy-cross"
# CMD="echo $1"
echo "Generate BSP"
rm src/board.py
tools/json2py.py < $BOARD > src/board.py

echo "ARCH = \"${BOARD%.*}\"" > src/hw/arch.py

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
        $MPY_CROSS $_f
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

for _lib in ${HTMLS[@]}; do
    if [ $_lib != '.' ]; then
        $CMD rmdir $_lib &> /dev/null
        echo "Create dir $_lib"
        $CMD mkdir $_lib
    fi

    for _f in ./$_lib/*.html; do
        _rf="$_lib/$(basename $_f)"
        echo "copying HTML $_f -> $_rf"
        $CMD put $_f $_rf
    done
    
    for _f in ./$_lib/*.js; do
        _rf="$_lib/$(basename $_f)"
        echo "copying JS $_f -> $_rf"
        $CMD put $_f $_rf
    done
    
    for _f in ./$_lib/*.css; do
        _rf="$_lib/$(basename $_f)"
        echo "copying CSS $_f -> $_rf"
        $CMD put $_f $_rf
    done
done

$CMD put static/favicon.ico static/favicon.ico
echo "Pushing FW-UPD host restrictions"
$CMD rmdir data &> /dev/null
$CMD mkdir data &> /dev/null
$CMD put src/fwupd.hosts data/fwupd.hosts

echo "Reset board"
# $CMD reset
