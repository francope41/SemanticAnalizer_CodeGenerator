#!/bin/sh
if [ $# -eq 0 ]
  then
    echo "Path to file required to run (EXAMPLE: \"./exec.sh ../samples/badbool.frag\")"
else
if test -f "../workdir/t1.s"
  then
    rm ../workdir/t1.s
  fi
  python3 ../main.py $1
  if test -f "t1.s"
    then
      cd ../pp3-post/spim
      ./spim -file ../../workdir/t1.s
      #./spim -file /home/eulo/Documents/UTSA/CodeGen/SemanticAnalizer_CodeGenerator/pp3-post/samples/t1.s
      
      #rm ../../workdir/t1.s

    fi
    
fi

