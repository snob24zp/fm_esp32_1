#!/bin/bash
. ./tools/esp-idf/export.sh

BOARD=esp32.json

SRCS=(hw "hw/${BOARD%.*}" net uclient .)
HTMLS=(static)
OUT_DIR=fw.tmp
FS_FILE=out/bins/fw.fs
MPY_CROSS=tools/mpy-cross

RELEASE="R$(date +%y%m%d)"

cd tools/micropython_a9_gprs/ports/esp32/boards/FARM_MONITOR
rm -rf fw.tmp
ln -s ../../../../../../bootloader fw.tmp
rm -rf gsm0710
ln -s ../../../../../../src/net/gsm0710 gsm0710
cd ../../

echo "Cleaning Micropython repository"
make BOARD=FARM_MONITOR clean
echo "Building Micropython (submodules)"
make submodules
echo "Building Micropython (Binary)"
make BOARD=FARM_MONITOR
cd ../../../..
mkdir -p out/bins 
cp tools/micropython_a9_gprs/ports/esp32/build-FARM_MONITOR/micropython.elf out/bins/micropython.elf
cp tools/micropython_a9_gprs/ports/esp32/build-FARM_MONITOR/micropython.bin out/bins/micropython.bin
cp tools/micropython_a9_gprs/ports/esp32/build-FARM_MONITOR/partition_table/partition-table.bin out/bins/partition-table.bin
cp tools/micropython_a9_gprs/ports/esp32/build-FARM_MONITOR/bootloader/bootloader.elf out/bins/bootloader.elf
cp tools/micropython_a9_gprs/ports/esp32/build-FARM_MONITOR/bootloader/bootloader.bin out/bins/bootloader.bin

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


echo "Creating littleFS filesystem image (sz: 2097152)"

mkdir -p out
rm -f $FS_FILE
./tools/mklittlefs -d 5 -c $OUT_DIR -s 2097152 $FS_FILE
rm -rf $OUT_DIR

# echo "Size: $(du -sb $FS_FILE)"

# echo "Creating UEBA bootloader firmware"
# tools/ueba/ueba-fw-builder -ib $FS_FILE -t dev_ar -o out/AR.FW
# echo "Use this file to update device: "
# ls -la out/*.uebf

tools/esputil mkhex 0 out/bins/bootloader.bin 0x8000 out/bins/partition-table.bin 0x10000 out/bins/micropython.bin 0x200000 $FS_FILE > out/bins/AR.$RELEASE.hex
#tools/esputil -p /dev/ttyACM0 -b 460800 flash out/bins/AR.*.hex

# python -m esptool --chip esp32c3 -b 460800 --before default_reset --after hard_reset --no-stub write_flash --flash_mode dio --flash_size 4MB --flash_freq 80m \
#           0x0 build-FARM_MONITOR/bootloader/bootloader.bin 0x8000 build-FARM_MONITOR/partition_table/partition-table.bin 0x10000 build-FARM_MONITOR/micropython.bin