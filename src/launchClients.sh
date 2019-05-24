#!/bin/bash

if [ -z "$1" ]
then
    echo "No arguments suplied (count of client to launch)"
    exit
else
    END=$1
fi

exec 1>2

for ((i=0; i < END; i++))
do
    python3 client.py &
    pids[${i}]=$!
done

exec &>$(tty)

read -t 3 -n 1
if [ $? = 0 ] ; then
    echo "closing pids"
    # wait for all pids
    for pid in ${pids[*]}; do
        echo "closing" + $pid
        kill -9 $pid
    done
fi


