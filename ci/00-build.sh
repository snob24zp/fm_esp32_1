#!/bin/bash
cd src
. /etc/profile.d/vega-tests.sh
. "$IDF_PATH"/export.sh


_minify() {
    echo "Minify folder: $1"
    for f in $@
    do
        echo "Converting: $f"
        minify $f > "main/$(basename -- $f)"
    done
}

HTML="../html/*.html"
CSS="../html/*.css"
_minify "${HTML[@]}"
_minify "${CSS[@]}"

idf.py all
idf.py partition_table
idf.py size

ls -l build/ltc-esp.elf
if [ $? -ne 0 ]; then
    exit $?
fi

rm ../out/factory-build.zip
./factory-create.sh
ls -l ../out/factory-build.zip
if [ $? -ne 0 ]; then
    exit $?
fi

cd ..
mkdir -p out
cd out
dotnet "$UEBA_PATH"/ueba-fw-builder.dll -ib ../src/build/ltc-esp.bin -t dev_ltc_c3 -o dev_ltc_c3
ls -l dev_ltc_c3.latest.uebf
exit $?
