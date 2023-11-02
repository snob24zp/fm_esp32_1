#!/bin/bash

mkdir -p out
ls -la src/
python3 -m pylint --ignore-imports y --import-graph out/imports.gv --max-line-length 160 --output out/code-check.log src/
exit 0