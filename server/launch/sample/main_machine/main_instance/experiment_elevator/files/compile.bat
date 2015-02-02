:: Synthesize. Builds the NGC file, which is later taken by ngdbuild.
xst -intstyle ise -ifn base.xst -ofn base.syr

:: Implement design
ngdbuild -intstyle ise -dd _ngo -nt timestamp -uc FPGA_2012_2013_def.ucf -p xc3s1000-ft256-4 base.ngc base.ngd
map -intstyle ise -p xc3s1000-ft256-4 -cm area -ir off -pr off -c 100 -o base_map.ncd base.ngd base.pcf
par -w -intstyle ise -ol high -t 1 base_map.ncd base.ncd base.pcf

:: The following command is part of Implement Design, but is reportedly not mandatory.
trce -intstyle ise -v 3 -s 4 -n 3 -fastpaths -xml base.twx base.ncd -o base.twr base.pcf

:: Generate programming file
bitgen -intstyle ise -f base.ut base.ncd