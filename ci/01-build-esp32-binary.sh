#!/bin/bash

RELEASE="R$(date +%y%m%d)"

./tools/esp-idf/install.sh
./build_fw_esp32c3.sh
wget -q -O out/bins/esputil.exe https://github.com/cpq/esputil/releases/latest/download/esputil.exe
wget -q -O out/bins/esputil https://github.com/cpq/esputil/releases/latest/download/esputil_linux
chmod 0755 out/bins/esputil

cp ci/burn.sh out/bins/burn.sh
cp ci/burn.bat out/bins/burn.bat

cd out
zip -r "AR.BINS.$RELEASE.zip" bins
cp AR.BINS.$RELEASE.zip AR.BINS.latest.zip