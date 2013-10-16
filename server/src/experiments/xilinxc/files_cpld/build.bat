xst -intstyle ise -ifn base.xst -ofn base.syr
if %errorlevel% neq 0 exit /b %errorlevel%


REM On Linux this is extremely important. Not cleaning the work folder after usage means that
REM the next user will potentially use code from the previous one, especially if he makes a mistake,
REM and it will go unnoticed by the system. Cleaning this folder forces the synthesization process
REM to really start anew, without reusing anything.
RD /S /Q "xst/work"

ngdbuild -intstyle ise -dd _ngo -uc cpld_weblab_res.ucf -p xc9572-PC84-7 base.ngc base.ngd
if %errorlevel% neq 0 exit /b %errorlevel%

cpldfit -intstyle ise -p xc9572-7-PC84 -ofmt vhdl -optimize speed -htmlrpt -loc on -slew fast -init low -inputs 36 -pterms 25 -power std -localfbk -pinfbk base.ngd
if %errorlevel% neq 0 exit /b %errorlevel%

hprep6 -s IEEE1149 -n base -i base
if %errorlevel% neq 0 exit /b %errorlevel%