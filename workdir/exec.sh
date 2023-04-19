#!/bin/sh
if [ $# -eq 0 ]
  then
    echo "Path to file required to run (EXAMPLE: \"./exec.sh ../samples/badbool.frag\")"
else
    python3 ../main.py $1
    if test -f "t1.s"
      then
        cd ../pp3-post/spim
        ls
        ./spim -file ../../workdir/t1.s
        
        rm ../../workdir/t1.s

    fi
    
fi

