#!/bin/bash

# 250-299
# 200-249
#

max=300
for ((i=258; i < $max; i++)); do
    value=$(($i*100))
    python3 knp_dumps.py $value 1
done