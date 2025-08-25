@echo off
setlocal enabledelayedexpansion
cls
color 0B
title LAN Screen Streamer v1.0 - Open Source Edition

:: Set paths relative to the batch file location
set "SCRIPT_DIR=%~dp0"
set "DATA_DIR=%SCRIPT_DIR%data\"
set "SCRIPTS_DIR=%DATA_DIR%scripts\"
set "CONFIG_DIR=%DATA_DIR%config\"
set "LOGS_DIR=%DATA_DIR%logs\"

:: Create directories if they don't exist
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
if not exist "%SCRIPTS_DIR%" mkdir "%SCRIPTS_DIR%"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

:MENU
cls
echo.
echo    ==================================================================
echo                      LAN SCREEN STREAMER v1.0
echo                        OPEN SOURCE EDITION
echo.
echo         Designed and Developed with LOVE by Kishnanda
echo                   For Streamers, By Streamers
echo    ==================================================================
echo.
echo                         [MAIN OPTIONS]
echo.
echo        [1] SENDER MODE    - Stream this PC's screen
echo        [2] RECEIVER MODE  - Display stream from another PC
echo.
echo                         [QUICK TOOLS]
echo.
echo        [3] Audio Setup    - Configure audio devices
echo        [4] System Check   - Verify installation
echo        [5] Help          - View instructions
echo        [6] Exit          - Close application
echo.
echo    ==================================================================
echo.
set /p choice="    Select option [1-6]: "

if "%choice%"=="1" goto SENDER
if "%choice%"=="2" goto RECEIVER  
if "%choice%"=="3" goto AUDIO_SETUP
if "%choice%"=="4" goto SYSTEM_CHECK
if "%choice%"=="5" goto HELP
if "%choice%"=="6" goto EXIT

echo.
echo    [!] Invalid option. Please try again.
timeout /t 2 >nul
goto MENU

:SENDER
cls
echo.
echo    ==================================================================
echo                         SENDER MODE
echo    ==================================================================
echo.

:: Find Python dynamically
call :FIND_PYTHON
if "!PYTHON_CMD!"=="" goto NO_PYTHON

echo    Checking configuration...
echo.

:: Check if this is first run
set "IS_FIRST_RUN=YES"
if exist "%CONFIG_DIR%stream_config.json" (
    !PYTHON_CMD! -c "import json; data=json.load(open(r'%CONFIG_DIR%stream_config.json')); exit(0 if data.get('first_run', True) else 1)" 2>nul
    if !errorlevel!==1 set "IS_FIRST_RUN=NO"
)

if "!IS_FIRST_RUN!"=="YES" goto FIRST_TIME_SETUP
if "!IS_FIRST_RUN!"=="NO" goto RETURNING_USER

:FIRST_TIME_SETUP
echo    Welcome! Let's set up your streaming preferences.
echo    ==================================================================
echo.
echo    We'll configure:
echo    1. Receiver IP address
echo    2. Audio device selection
echo    3. Resolution settings
echo    4. Quality preferences
echo.
echo    This is a one-time setup. Your preferences will be saved.
echo.
echo    ==================================================================
echo.
timeout /t 2 >nul

:: Run sender with first-time setup
!PYTHON_CMD! "%SCRIPTS_DIR%sender_enhanced.py" --first-run
goto AFTER_SENDER

:RETURNING_USER
echo    Welcome back! Quick Connect Options:
echo    ==================================================================
echo.

:: Display last settings
!PYTHON_CMD! -c "import sys; sys.path.insert(0, r'%SCRIPTS_DIR%'); from settings_manager import get_settings; s=get_settings(); s.display_current_settings()" 2>nul

echo.
echo    [ENTER] Connect with last settings
echo    [1]     Change receiver IP
echo    [2]     Change audio device
echo    [3]     Change resolution
echo    [4]     Change quality
echo    [5]     Full setup (reconfigure all)
echo    [M]     Return to menu
echo.
set /p quick_choice="    Select option (or press ENTER for quick connect): "

if "!quick_choice!"=="" (
    :: Quick connect with last settings
    echo.
    echo    Connecting with last settings...
    !PYTHON_CMD! "%SCRIPTS_DIR%sender_enhanced.py" --quick
) else if "!quick_choice!"=="1" (
    !PYTHON_CMD! "%SCRIPTS_DIR%sender_enhanced.py" --change-ip
) else if "!quick_choice!"=="2" (
    !PYTHON_CMD! "%SCRIPTS_DIR%sender_enhanced.py" --change-audio
) else if "!quick_choice!"=="3" (
    !PYTHON_CMD! "%SCRIPTS_DIR%sender_enhanced.py" --change-resolution
) else if "!quick_choice!"=="4" (
    !PYTHON_CMD! "%SCRIPTS_DIR%sender_enhanced.py" --change-quality
) else if "!quick_choice!"=="5" (
    !PYTHON_CMD! "%SCRIPTS_DIR%sender_enhanced.py" --full-setup
) else if /i "!quick_choice!"=="M" (
    goto MENU
) else (
    echo    Invalid option. Starting with full setup...
    !PYTHON_CMD! "%SCRIPTS_DIR%sender_enhanced.py" --full-setup
)

:AFTER_SENDER
echo.
echo    Press any key to return to menu...
pause >nul
goto MENU

:RECEIVER
cls
echo.
echo    ==================================================================
echo                         RECEIVER MODE
echo    ==================================================================
echo.
echo    Starting receiver...
echo.
echo    Features:
echo    -------------------------
echo    - Automatic sender detection
echo    - Audio output device selection
echo    - Fullscreen support (press F)
echo    - Connection history
echo.
echo    Your IP address will be displayed for the sender.
echo.
echo    Controls during streaming:
echo    - F or F11: Toggle fullscreen
echo    - Q or ESC: Stop receiving
echo    - +/-: Adjust volume
echo    - Space: Pause/Resume
echo.
echo    ==================================================================
echo.
echo    Detecting Python...

:: Find Python dynamically
call :FIND_PYTHON
if "!PYTHON_CMD!"=="" goto NO_PYTHON

echo    Using Python: !PYTHON_CMD!
echo.

:: Run receiver script
if exist "%SCRIPTS_DIR%receiver_with_audio_selection.py" (
    echo    Starting enhanced receiver with audio selection...
    !PYTHON_CMD! "%SCRIPTS_DIR%receiver_with_audio_selection.py"
) else (
    echo    ERROR: Receiver script not found!
    echo    Please ensure data\scripts\receiver_with_audio_selection.py exists
)

echo.
echo    Press any key to return to menu...
pause >nul
goto MENU

:AUDIO_SETUP
cls
echo.
echo    ==================================================================
echo                      AUDIO SETUP WIZARD
echo    ==================================================================
echo.
echo    This wizard will help you configure audio devices for streaming.
echo.
echo    Detecting Python...

:: Find Python dynamically
call :FIND_PYTHON
if "!PYTHON_CMD!"=="" goto NO_PYTHON

echo    Using Python: !PYTHON_CMD!
echo.

if exist "%SCRIPTS_DIR%audio_setup_wizard.py" (
    !PYTHON_CMD! "%SCRIPTS_DIR%audio_setup_wizard.py"
) else (
    echo    Audio setup wizard not found!
    echo    Please ensure data\scripts\audio_setup_wizard.py exists
)

echo.
echo    Press any key to return to menu...
pause >nul
goto MENU

:SYSTEM_CHECK
cls
echo.
echo    ==================================================================
echo                      SYSTEM CHECK
echo    ==================================================================
echo.
echo    Checking system requirements and dependencies...
echo.

:: Find Python dynamically
call :FIND_PYTHON
if "!PYTHON_CMD!"=="" (
    echo    [!] Python not found!
    echo        Please install Python 3.8 or higher from python.org
    goto INSTALL_PROMPT
)

echo    [✓] Python found: !PYTHON_CMD!
echo.

:: Check Python version
!PYTHON_CMD! --version
echo.

if exist "%SCRIPTS_DIR%system_check.py" (
    !PYTHON_CMD! "%SCRIPTS_DIR%system_check.py"
) else (
    echo    Performing basic checks...
    echo.
    !PYTHON_CMD! -c "import sys; print(f'    Python version: {sys.version}')"
    echo.
    echo    Checking required packages...
    !PYTHON_CMD! -m pip list 2>nul | findstr /i "opencv-python numpy Pillow dxcam mss sounddevice pyaudio"
    if errorlevel 1 (
        echo.
        echo    [!] Some packages may be missing.
        echo        Run: pip install -r requirements.txt
    ) else (
        echo    [✓] Core packages found
    )
)

echo.
echo    Press any key to return to menu...
pause >nul
goto MENU

:HELP
cls
echo.
echo    ==================================================================
echo                      HELP & INSTRUCTIONS
echo    ==================================================================
echo.
echo    QUICK START GUIDE:
echo    ------------------
echo    1. On the PC you want to stream FROM:
echo       - Select option [1] SENDER MODE
echo       - Note the IP address shown
echo.
echo    2. On the PC/device you want to stream TO:
echo       - Select option [2] RECEIVER MODE
echo       - Enter the sender's IP when prompted
echo.
echo    REQUIREMENTS:
echo    -------------
echo    - Both devices must be on the same network
echo    - Windows 10/11 recommended
echo    - Python 3.8+ (will auto-install if missing)
echo.
echo    TROUBLESHOOTING:
echo    ----------------
echo    - Black screen: Run as Administrator
echo    - No connection: Check firewall settings
echo    - No audio: Run Audio Setup (option 3)
echo    - Lag: Use ethernet instead of WiFi
echo.
echo    KEYBOARD SHORTCUTS:
echo    -------------------
echo    During streaming:
echo    - Q: Quit/Stop
echo    - F: Fullscreen (receiver only)
echo    - Space: Pause/Resume
echo    - +/-: Volume control
echo.
echo    For more help, see README.md or visit our GitHub page.
echo.
echo    ==================================================================
echo.
echo    Press any key to return to menu...
pause >nul
goto MENU

:INSTALL_PROMPT
echo.
echo    ==================================================================
echo                    PYTHON INSTALLATION REQUIRED
echo    ==================================================================
echo.
echo    Python is not installed on your system.
echo.
echo    Would you like to:
echo    1. Automatically download and install Python
echo    2. Get instructions for manual installation
echo    3. Return to menu
echo.
set /p install_choice="    Select option [1-3]: "

if "%install_choice%"=="1" goto AUTO_INSTALL_PYTHON
if "%install_choice%"=="2" goto MANUAL_INSTALL_INFO
goto MENU

:AUTO_INSTALL_PYTHON
echo.
echo    Downloading Python installer...
echo.
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile '%TEMP%\python_installer.exe'}"

if exist "%TEMP%\python_installer.exe" (
    echo    Installing Python...
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1
    echo    Installation complete! Please restart this program.
    del "%TEMP%\python_installer.exe"
) else (
    echo    Download failed. Please install manually.
)
pause
goto MENU

:MANUAL_INSTALL_INFO
echo.
echo    ==================================================================
echo                    MANUAL INSTALLATION INSTRUCTIONS
echo    ==================================================================
echo.
echo    1. Visit: https://www.python.org/downloads/
echo    2. Download Python 3.12 or newer
echo    3. Run the installer
echo    4. IMPORTANT: Check "Add Python to PATH"
echo    5. Click "Install Now"
echo    6. Restart this program after installation
echo.
echo    ==================================================================
echo.
pause
goto MENU

:FIND_PYTHON
:: Reset Python command
set "PYTHON_CMD="

:: Method 1: Try py launcher (most reliable on Windows)
where py >nul 2>&1
if !errorlevel!==0 (
    py -c "import sys" >nul 2>&1
    if !errorlevel!==0 (
        set "PYTHON_CMD=py"
        goto :eof
    )
)

:: Method 2: Try python command
where python >nul 2>&1
if !errorlevel!==0 (
    :: Test if it's real Python or Windows Store redirect
    python -c "import sys" >nul 2>&1
    if !errorlevel!==0 (
        set "PYTHON_CMD=python"
        goto :eof
    )
)

:: Method 3: Try python3 command
where python3 >nul 2>&1
if !errorlevel!==0 (
    python3 -c "import sys" >nul 2>&1
    if !errorlevel!==0 (
        set "PYTHON_CMD=python3"
        goto :eof
    )
)

:: Method 4: Check common Python installation directories
:: Check user's local AppData (most common on Windows)
for %%v in (312 311 310 39 38) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%v\python.exe" (
        set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python%%v\python.exe"
        goto :eof
    )
)

:: Check system-wide installations
for %%v in (312 311 310 39 38) do (
    if exist "C:\Python%%v\python.exe" (
        set "PYTHON_CMD=C:\Python%%v\python.exe"
        goto :eof
    )
)

:: Check Program Files
for %%v in (312 311 310 39 38) do (
    if exist "%ProgramFiles%\Python%%v\python.exe" (
        set "PYTHON_CMD=%ProgramFiles%\Python%%v\python.exe"
        goto :eof
    )
    if exist "%ProgramFiles(x86)%\Python%%v\python.exe" (
        set "PYTHON_CMD=%ProgramFiles(x86)%\Python%%v\python.exe"
        goto :eof
    )
)

:: Check for Anaconda/Miniconda
if exist "%USERPROFILE%\Anaconda3\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\Anaconda3\python.exe"
    goto :eof
)
if exist "%USERPROFILE%\Miniconda3\python.exe" (
    set "PYTHON_CMD=%USERPROFILE%\Miniconda3\python.exe"
    goto :eof
)

:: Check AppData\Local\Microsoft\WindowsApps (Microsoft Store Python)
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    :: Test if it's actually installed
    "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" -c "import sys" >nul 2>&1
    if !errorlevel!==0 (
        set "PYTHON_CMD=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
        goto :eof
    )
)

:: Python not found
goto :eof

:NO_PYTHON
echo.
echo    ==================================================================
echo                         ERROR: PYTHON NOT FOUND
echo    ==================================================================
echo.
echo    Python is required to run this application.
echo.
echo    Tried the following:
echo    - py launcher
echo    - python command
echo    - python3 command
echo    - Common installation directories
echo    - User AppData folders
echo.
echo    Please install Python 3.8 or higher from:
echo    https://www.python.org/downloads/
echo.
echo    Make sure to check "Add Python to PATH" during installation!
echo.
echo    ==================================================================
echo.
echo    Press any key to return to menu...
pause >nul
goto MENU

:EXIT
cls
echo.
echo    ==================================================================
echo                      THANK YOU FOR USING
echo                     LAN SCREEN STREAMER v1.0
echo.
echo         Designed and Developed with LOVE by Kishnanda
echo                   For Streamers, By Streamers
echo    ==================================================================
echo.
echo    If you enjoyed this software, please:
echo    - ⭐ Star our GitHub repository
echo    - 🐛 Report any bugs you find
echo    - 💡 Suggest new features
echo    - 🤝 Contribute to the project
echo.
echo    GitHub: https://github.com/yourusername/LAN-Streamer-Project
echo.
echo    ==================================================================
echo.
timeout /t 3 >nul
exit /b 0
