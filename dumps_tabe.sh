#!/bin/bash

#python3 knp_dumps.py $i
# 3 
# 387

max=30
for ((i=25; i < $max; i++)); do
    value=$(($i*100))
    python3 knp_dumps.py $value 2
done


# 左上 20-24 25-29
# 左下 30-36