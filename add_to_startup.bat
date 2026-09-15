@echo off
setlocal
cd /d "%~dp0"

set "TARGET_BAT=%~dp0run_desktop_notifier.bat"
set "SHORTCUT_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\WaterReminder.lnk"

powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%TARGET_BAT%'; $s.WorkingDirectory = '%~dp0'; $s.WindowStyle = 7; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo.
    echo =========================================================
    echo  [SUCCESS] Water Reminder added to Windows Startup!
    echo  It will now launch automatically whenever your laptop powers on.
    echo =========================================================
) else (
    echo.
    echo [ERROR] Failed to create startup shortcut.
)
echo.
pause
