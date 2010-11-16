
@echo off

@setlocal enableextensions
@cd /d "%~dp0"

REM The following directory is for .NET 2.0
set DOTNETFX2=%SystemRoot%\Microsoft.NET\Framework\v2.0.50727

REM The following directory is for .NET 4
set DOTNETFX4=%SystemRoot%\Microsoft.NET\Framework\v4.0.30319

set PATH=%PATH%;%DOTNETFX4%

echo Installing Weblab Windows VNC Service...
echo ---------------------------------------------------
InstallUtil /u WindowsVNCService.exe
echo ---------------------------------------------------
echo Done.
pause
