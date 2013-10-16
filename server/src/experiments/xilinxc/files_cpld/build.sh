#!/bin/bash
# Force an exit if any command returns non-zero (error code).
set -e 

xst -intstyle ise -ifn weblab.xst -ofn weblab.syr

ngdbuild -intstyle ise -dd _ngo -uc weblab_res.ucf -p xc9572-PC84-7 weblab.ngc weblab.ngd

cpldfit -intstyle ise -p xc9572-7-PC84 -ofmt vhdl -optimize speed -htmlrpt -loc on -slew fast -init low -inputs 36 -pterms 25 -power std -localfbk -pinfbk weblab.ngd

hprep6 -s IEEE1149 -n weblab -i weblab