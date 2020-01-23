#!/bin/bash

# 
#

max=20
for ((i=12; i < $max; i++)); do
    value=$(($i*100))
    python3 knp_dumps.py $value 3
done