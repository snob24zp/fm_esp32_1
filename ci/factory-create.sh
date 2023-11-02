#!/bin/bash

mkdir -p ../out
mkdir ../out/factory-build
cp build/ota_data_initial.bin ../out/factory-build/ota_data_initial.bin
cp build/bootloader/bootloader.bin ../out/factory-build/bootloader.bin
cp build/ltc-esp.bin ../out/factory-build/ltc-esp.bin
cp build/partition_table/partition-table.bin ../out/factory-build/partition-table.bin
cp build/phy_init_data.bin ../out/factory-build/phy_init_data.bin

mkdir ../out/factory-build/esp-tool-linux
cp ../esp-tool-linux/* ../out/factory-build/esp-tool-linux/

echo "#/bin/bash" > ../out/factory-build/flash.sh
echo "esp-tool-linux/esptool -b 460800 --before default_reset --after hard_reset --chip esp32c3 --no-stub write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x0 bootloader.bin 0x8000 partition-table.bin 0xd000 ota_data_initial.bin 0x10000 ltc-esp.bin" >> ../out/factory-build/flash.sh
chmod 0755 ../out/factory-build/flash.sh

mkdir ../out/factory-build/esp-tool-windows
cp -r ../esp-tool-windows/* ../out/factory-build/esp-tool-windows/
echo "esp-tool-windows\\esptool.exe -b 460800 --before default_reset --after hard_reset --chip esp32c3 --no-stub write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x0 bootloader.bin 0x8000 partition-table.bin 0xd000 ota_data_initial.bin 0x10000 ltc-esp.bin" >> ../out/factory-build/flash.bat

ln -s ../out/factory-build/ factory-build
zip -r ../out/factory-build.zip factory-build

rm -rf ../out/factory-build
rm factory-build