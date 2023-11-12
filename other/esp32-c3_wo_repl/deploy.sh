#!/bin/bash
esptool.py -p /dev/ttyACM0 -b 460800 --before=default_reset --after=hard_reset --no-stub write_flash --flash_mode dio --flash_freq 80m --flash_size 4MB 0x0 bootloader.bin 0x10000 micropython.bin 0x8000 partition-table.bin

