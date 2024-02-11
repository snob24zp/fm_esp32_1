#!/bin/bash

python3 -m pip install markdown jinja2

DOC_DIR="./doc"

mkdir -p ./data
mkdir -p ./out
mkdir -p ./out/docs


python3 ./ci/gen_doc.py