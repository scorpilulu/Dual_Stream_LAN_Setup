@echo off
setlocal enabledelayedexpansion
cls
color 0A
title LAN Screen Streamer - Setup Wizard

echo.
echo    ==================================================================
echo                  LAN SCREEN STREAMER SETUP WIZARD
echo                            Version 1.0
echo    ==================================================================
echo.
echo    This wizard will set up LAN Screen Streamer on your computer.
echo.
echo    The following will be installed/configured:
echo    - Python 3.8+ (if not already installed)
echo    - Required Python packages
echo    - Application shortcuts
echo.
echo    ==================================================================
echo.
pause

:: Check for Python
echo.
echo    [1/3] Checking for Python installation...
echo.

:: Try py launcher first (most reliable)
where py >nul 2>&1
if !errorlevel!==0 (
    py -c "import sys" >nul 2>&1
    if !errorlevel!==0 (
        echo    [✓] Python launcher found!
        set "PYTHON_CMD=py"
        goto CHECK_VERSION
    )
)

:: Try python command
where python >nul 2>&1
if !errorlevel!==0 (
    python -c "import sys" >nul 2>&1
    if !errorlevel!==0 (
        echo    [✓] Python found!
        set "PYTHON_CMD=python"
        goto CHECK_VERSION
    )
)

:: Try python3 command
where python3 >nul 2>&1
if !errorlevel!==0 (
    python3 -c "import sys" >nul 2>&1
    if !errorlevel!==0 (
        echo    [✓] Python found!
        set "PYTHON_CMD=python3"
        goto CHECK_VERSION
    )
)

echo    [!] Python not found. Would you like to install it automatically?
set /p install_python="    Install Python? (Y/N): "
if /i "%install_python%"=="Y" goto INSTALL_PYTHON
echo    Setup cannot continue without Python.
pause
exit /b 1

:INSTALL_PYTHON
echo.
echo    Downloading Python 3.12...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile '%TEMP%\python_installer.exe'}"

if exist "%TEMP%\python_installer.exe" (
    echo    Installing Python...
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del "%TEMP%\python_installer.exe"
    echo    [✓] Python installed successfully!
    set "PYTHON_CMD=python"
) else (
    echo    [!] Download failed. Please install Python manually from python.org
    pause
    exit /b 1
)

:CHECK_VERSION
echo.
echo    Checking Python version...
%PYTHON_CMD% -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" 2>nul
if %errorlevel%==0 (
    echo    [✓] Python version is compatible
) else (
    echo    [!] Python 3.8 or higher is required
    echo        Please upgrade Python from python.org
    pause
    exit /b 1
)

:: Install packages
echo.
echo    ==================================================================
echo.
echo    [2/3] Installing required packages...
echo.
echo    This may take a few minutes...
echo.

%PYTHON_CMD% -m pip install --upgrade pip >nul 2>&1
%PYTHON_CMD% -m pip install -r requirements.txt

if %errorlevel%==0 (
    echo    [✓] All packages installed successfully!
) else (
    echo    [!] Some packages failed to install.
    echo        Attempting individual installation...
    
    %PYTHON_CMD% -m pip install opencv-python
    %PYTHON_CMD% -m pip install numpy
    %PYTHON_CMD% -m pip install Pillow
    %PYTHON_CMD% -m pip install dxcam
    %PYTHON_CMD% -m pip install mss
    %PYTHON_CMD% -m pip install sounddevice
    %PYTHON_CMD% -m pip install PyAudio
    %PYTHON_CMD% -m pip install netifaces
)

:: Create desktop shortcut
echo.
echo    ==================================================================
echo.
echo    [3/3] Creating shortcuts...
echo.

set "desktop=%USERPROFILE%\Desktop"
set "shortcut=%desktop%\LAN Screen Streamer.lnk"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcut%'); $Shortcut.TargetPath = '%~dp0LAN_Streamer_1.0.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = 'shell32.dll,238'; $Shortcut.Description = 'LAN Screen Streamer v1.0'; $Shortcut.Save()"

if exist "%shortcut%" (
    echo    [✓] Desktop shortcut created!
) else (
    echo    [!] Could not create desktop shortcut
)

:: Final setup
echo.
echo    ==================================================================
echo                      SETUP COMPLETE!
echo    ==================================================================
echo.
echo    LAN Screen Streamer has been successfully installed!
echo.
echo    You can now:
echo    1. Double-click 'LAN_Streamer_1.0.bat' to start
echo    2. Use the desktop shortcut (if created)
echo    3. Run from Start Menu (coming soon)
echo.
echo    First time setup tips:
echo    - Run as Administrator for best performance
echo    - Allow through Windows Firewall when prompted
echo    - Check README.md for usage instructions
echo.
echo    ==================================================================
echo.
echo    Press any key to launch LAN Screen Streamer...
pause >nul

start "" "%~dp0LAN_Streamer_1.0.bat"
exit /b 0
