#!/bin/bash

BOARD=$1
if [ -z $1 ]; then
    BOARD=esp32.json
fi

git submodule init
git submodule sync

SRCS=(hw "hw/${BOARD%.*}" net uclient .)
HTMLS=(static)
OUT_DIR=fw.tmp
FS_FILE=out/fw.fs
MPY_CROSS=tools/mpy-cross

mkdir -p $OUT_DIR
rm -rf $OUT_DIR/*

echo "Generate BSP"
rm src/board.py
jsonlint -Sf $BOARD | tools/json2py.py > src/board.py

echo "ARCH = \"${BOARD%.*}\"" > src/hw/arch.py
python3 src/version.py

for _lib in ${SRCS[@]}; do
    if [ $_lib != '.' ]; then
        echo "Create dir $_lib"
        mkdir -p "$OUT_DIR/$_lib"
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
            cp $_mpy "$OUT_DIR/$_rmpy"
            rm $_mpy
        else
            echo "copying $_f -> $_rf"
            cp $_f "$OUT_DIR/$_rf"
            if [ -f $_mpy ]; then
                rm $_mpy
            fi
        fi
    done
done

for _lib in ${HTMLS[@]}; do
    if [ $_lib != '.' ]; then
        echo "Create dir ./src/$_lib"
        mkdir -p "./src/$_lib"
        mkdir -p "$OUT_DIR/$_lib"
    fi

    for _f in ./$_lib/*.html; do
        _rf="$_lib/$(basename $_f)"
        _minified="./src/$_lib/$(basename $_f)"
        minify $_f > $_minified
        echo "copying HTML $_minified -> $_rf"
        cp $_minified "$OUT_DIR/$_rf"
    done
    
    for _f in ./$_lib/*.js; do
        _rf="$_lib/$(basename $_f)"
        _minified="./src/$_lib/$(basename $_f)"
        minify $_f > $_minified
        echo "copying JS $_minified -> $_rf"
        cp $_minified "$OUT_DIR/$_rf"
    done
    
    for _f in ./$_lib/*.css; do
        _rf="$_lib/$(basename $_f)"
        _minified="./src/$_lib/$(basename $_f)"
        minify $_f > $_minified
        echo "copying CSS $_minified -> $_rf"
        cp $_minified "$OUT_DIR/$_rf"
    done
done

cp static/favicon.ico "$OUT_DIR/static/favicon.ico"
ls -la $OUT_DIR/
sz=$(du -sb $OUT_DIR | cut -f 1)

echo "Creating littleFS filesystem image (sz: $sz)"

mkdir -p out
rm -f $FS_FILE
./tools/mklittlefs -d 5 -c $OUT_DIR -b 512 -s $(($sz + 8196)) $FS_FILE
rm -rf $OUT_DIR

echo "Size: $(du -sb $FS_FILE)"

echo "Creating UEBA bootloader firmware"
tools/ueba/ueba-fw-builder -ib $FS_FILE -t dev_ar -o out/AR.FW
echo "Use this file to update device: "
ls -la out/*.uebf