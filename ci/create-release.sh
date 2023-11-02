#!/bin/bash
CWD='.'

function create_releasefile {
        release="R$(date +%y%m%d)"
        commit=$(git rev-parse HEAD)
        branch=$(git rev-parse --abbrev-ref HEAD)
        fwfile="AR.latest.uebf"
        jo release=$release branch=$branch commit=$commit fwfile=$fwfile > "$CWD/release.json"
        cat "$CWD/release.json" | jq .
}

create_releasefile