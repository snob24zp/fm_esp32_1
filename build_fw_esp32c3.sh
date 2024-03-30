#!/bin/bash
. ./tools/esp-idf/export.sh

cd tools/micropython_a9_gprs/ports/esp32/boards/FARM_MONITOR
rm -rf fw.tmp
ln -s ../../../../../../src fw.tmp
cd ../../

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

# python -m esptool --chip esp32c3 -b 460800 --before default_reset --after hard_reset --no-stub write_flash --flash_mode dio --flash_size 4MB --flash_freq 80m \
#           0x0 build-FARM_MONITOR/bootloader/bootloader.bin 0x8000 build-FARM_MONITOR/partition_table/partition-table.bin 0x10000 build-FARM_MONITOR/micropython.bin