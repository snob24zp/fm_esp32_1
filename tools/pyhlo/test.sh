#!/bin/bash

for i in {1..20}
do
   echo "Test: $i"
   ./pyhlo.py -f ../../$(cat ../../config.json | jq -Mr  '.fw_file') -b $(cat ../../config.json | jq -Mr  '.broker.host') -d $(cat ../../config.json | jq -Mr  '.token')
   sleep 90
done
