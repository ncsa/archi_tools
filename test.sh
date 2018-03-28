#!/bin/sh
for f in acquire mkdb ingest list   dbinfo modelinfo  ; do
    cmd="./archi_tool.py $f"
    echo $cmd
    $cmd > /dev/null
    echo ========== ; done

 
