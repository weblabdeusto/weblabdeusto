#!/bin/bash
# Force an exit if any command returns non-zero (error code).
set -e 

xst -intstyle ise -ifn base.xst -ofn base.syr

ngdbuild -intstyle ise -dd _ngo -uc cpld_weblab_res.ucf -p xc9572-PC84-7 base.ngc base.ngd

cpldfit -intstyle ise -p xc9572-7-PC84 -ofmt vhdl -optimize speed -htmlrpt -loc on -slew fast -init low -inputs 36 -pterms 25 -power std -localfbk -pinfbk base.ngd

hprep6 -s IEEE1149 -n base -i base