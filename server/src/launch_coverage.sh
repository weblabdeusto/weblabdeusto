#!/bin/bash

if [ $# -gt 0 ]; then
   if [ $1 -eq "html" ]; then
      OUTPUT="html"
   else
      OUTPUT="report"
   fi
else
   OUTPUT="report"
fi
   
coverage run --branch launch_tests.py

coverage $OUTPUT --omit=test,$PWD/../lib,/usr,patcher,libraries,launch_tests,conf