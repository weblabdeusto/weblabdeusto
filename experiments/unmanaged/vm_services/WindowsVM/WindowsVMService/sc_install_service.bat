
@echo off

echo Installing Weblab Windows VM Service through the sc utility. If this fails, please try the other installer.
echo Note that once installed it is possible to manage the service as normally through either the Service Manager or the sc utility.
echo Now registering the new service under the name: WeblabVMService
echo ---------------------------------------------------
sc create WeblabVMService binpath= %cd%/WindowsVMService.exe
echo ---------------------------------------------------
echo Done.
pause
