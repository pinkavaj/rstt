#!/bin/sh

[ -d data ] || mkdir data

while [ "${1}" != "" ]; do
    fname="${1##.*/}"
    fname="data/${fname%\.frames}"
    echo $fname
    ./frame_dumper.py $1 $fname
    shift
done
