#!/bin/bash

python3 -m pip install --break-system-packages junit2html

UEBF_FW=AR.FW.latest.uebf
BINS_FW=AR.BINS.latest.zip
SRC_ZIP=AR.src.latest.zip

export CWD="/var/www/release/esp32-mpy-uclient/release-$(date +%y%m%d)"

function create_releasefile {
        release="R$(date +%y%m%d)"
        commit=$(git rev-parse HEAD)
        branch=$(git rev-parse --abbrev-ref HEAD)
        jo release=$release branch=$branch commit=$commit fwfile=$UEBF_FW > "$CWD/release.json"
        cat "$CWD/release.json" | jq .
}

rm -rf $CWD
ls -l artifacts
mkdir -p $CWD
mkdir -p "$CWD/html"
cp artifacts/lintcheck/code-check.log "$CWD/code-check.log"
# cp artifacts/factory-build.zip/factory-build.zip "$CWD/factory-build.zip"
cp artifacts/$UEBF_FW/$UEBF_FW "$CWD/$UEBF_FW"
cp artifacts/$BINS_FW/$BINS_FW "$CWD/$BINS_FW"
cp artifacts/$SRC_ZIP/$SRC_ZIP "$CWD/$SRC_ZIP"

./ci/release-page/gen.py "R$(date +%y%m%d)" "$(git rev-parse HEAD)" $(git rev-parse --abbrev-ref HEAD) > "$CWD/index.html"

create_releasefile

for f in ./artifacts/tests-summary/*.xml
do
         echo "Converting $f"
         /home/github/.local/bin/junit2html $f
done
mkdir -p "$CWD/tests"
cp -R ./artifacts/tests-summary/*.html  "$CWD/tests"
cp -R ./artifacts/docs-summary/* "$CWD/html"

# /opt/gen_rel 
# python3 /opt/updater_pub.py
