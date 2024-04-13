#!/bin/bash

mkdir tmp

mkdir -p tmp
mkdir -p tmp/AR-src

cp -rv src tmp/AR-src
mkdir -p tmp/AR-src/tools
cp -rv tools/ueba tmp/AR-src/tools
cp -rv tools/pyhlo tmp/AR-src/tools
cp -rv tools/esputil tmp/AR-src/tools
cp -rv tools/json2py.py tmp/AR-src/tools
cp -rv tools/mklittlefs tmp/AR-src/tools
cp -rv tools/mpy-cross tmp/AR-src/tools
cp -rv doc tmp/AR-src


OLD_PWD=$(pwd)
cd tmp/AR-src
tar -czvf $OLD_PWD/out/AR.src.tar.gz *
cd $OLD_PWD

rm -rf tmp

