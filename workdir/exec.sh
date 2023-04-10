#!/bin/sh
if [ $# -eq 0 ]
  then
    echo "Path to file required to run (EXAMPLE: \"./exec.sh ../samples/badbool.frag\")"
else
    python ../main.py $1
fi