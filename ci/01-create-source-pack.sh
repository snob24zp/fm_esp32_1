#!/bin/bash

rm -rf out/AR.src.zip

mkdir -p out
mkdir out/srcpack
mkdir -p out/srcpack

cp -rv src out/srcpack
mkdir -p out/srcpack/tools
cp -rv tools/ueba out/srcpack/tools
cp -rv tools/pyhlo out/srcpack/tools
cp -rv tools/esputil out/srcpack/tools
cp -rv tools/json2py.py out/srcpack/tools
cp -rv tools/mklittlefs out/srcpack/tools
cp -rv tools/mpy-cross out/srcpack/tools
cp -rv doc out/srcpack

cd out
zip -r "AR.src.latest.zip" srcpack
cd ..

rm -rf out/srcpack