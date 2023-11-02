#!/bin/bash


export CWD="/var/www/release/ltc-c3/release-$(date +%y%m%d)"

function create_releasefile {
        release="R$(date +%y%m%d)"
        commit=$(git rev-parse HEAD)
        branch=$(git rev-parse --abbrev-ref HEAD)
        fwfile="dev_ltc_c3.latest.uebf"
        jo release=$release branch=$branch commit=$commit fwfile=$fwfile > "$CWD/release.json"
        cat "$CWD/release.json" | jq .
}

rm -rf $CWD
ls -l artifacts
mkdir -p $CWD
mkdir -p "$CWD/html"
mkdir -p "$CWD/cppcheck"
cp -r ./doc/html/html/ "$CWD/html/"
tar -xzf artifacts/cppcheck/cppcheck.tar.gz -C "$CWD/cppcheck"
cp artifacts/serial.log/serial.log "$CWD/serial.log"
cp artifacts/factory-build.zip/factory-build.zip "$CWD/factory-build.zip"
cp artifacts/dev_ltc_c3.latest.uebf/dev_ltc_c3.latest.uebf "$CWD/dev_ltc_c3.latest.uebf"
./ci/release-page/gen.py "R$(date +%y%m%d)" "$(git rev-parse HEAD)" $(git rev-parse --abbrev-ref HEAD) > "$CWD/index.html"

create_releasefile

for f in ./artifacts/tests-summary/*.xml
do
        echo "Converting $f"
        junit2html $f
done
mkdir -p "$CWD/tests"
cp -R ./artifacts/tests-summary/*.html  "$CWD/tests"

/opt/ltc_gen_rel
python3 /opt/updater_pub.py
