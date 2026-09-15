@echo off
echo Stopping any running Water Reminder desktop background processes...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'desktop_notifier\.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host ('Terminated process ' + $_.ProcessId) }"
echo.
echo Stopped.
pause
