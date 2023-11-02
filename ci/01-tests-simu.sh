#!/bin/bash
TEST_DIR="./tests/[0-9]*"

python3 -m pip install --break-system-packages -r ./tests/requirements.txt

mkdir -p ./data
mkdir -p ./out
mkdir -p ./out/tests

mkdir -p /var/www/release/esp32-mpy-uclient
ls -la out
ls -la /var/www/release
cp -v out/AR.FW.latest.uebf /var/www/release/esp32-mpy-uclient/

export ret=0
for f in $TEST_DIR
do
    if [ -x "$f" ]; then
        echo "-----  Start test [$f]  -----"
        python3 $f
        ret=$?
        if [ $ret -ne 0 ]; then
            echo "Test fails with code: $ret"
            break
        fi
        echo "-----  Test [$f] is done  -----"
        sleep 2
    fi
done

exit $ret