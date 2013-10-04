xst -intstyle ise -ifn cpld_weblab.xst -ofn cpld_weblab.syr

ngdbuild -intstyle ise -dd _ngo -uc cpld_weblab_res.ucf -p xc9572-PC84-7 cpld_weblab.ngc cpld_weblab.ngd

cpldfit -intstyle ise -p xc9572-7-PC84 -ofmt vhdl -optimize speed -htmlrpt -loc on -slew fast -init low -inputs 36 -pterms 25 -power std -localfbk -pinfbk cpld_weblab.ngd

hprep6 -s IEEE1149 -n cpld_weblab -i cpld_weblab