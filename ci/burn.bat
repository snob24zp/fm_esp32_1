@echo off
set /p "id=Enter COM port: "

esputil -p %id% -b 460800 flash out/bins/AR.*.hex