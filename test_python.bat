@echo off
setlocal enabledelayedexpansion
echo Testing Python detection...
echo.

:: Method 1: py launcher
echo Checking py launcher...
where py >nul 2>&1
if !errorlevel!==0 (
    echo [FOUND] py command exists
    py --version
    py -c "import sys; print(f'  Executable: {sys.executable}')"
) else (
    echo [MISSING] py command not found
)
echo.

:: Method 2: python command  
echo Checking python command...
where python >nul 2>&1
if !errorlevel!==0 (
    echo [FOUND] python command exists
    python --version 2>&1
) else (
    echo [MISSING] python command not found
)
echo.

:: Method 3: python3 command
echo Checking python3 command...
where python3 >nul 2>&1
if !errorlevel!==0 (
    echo [FOUND] python3 command exists
    python3 --version
) else (
    echo [MISSING] python3 command not found
)
echo.

:: Method 4: Common paths
echo Checking common installation paths...
set "found_paths="

for %%v in (312 311 310 39 38) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%v\python.exe" (
        echo [FOUND] %LOCALAPPDATA%\Programs\Python\Python%%v\python.exe
        set "found_paths=1"
    )
)

for %%v in (312 311 310 39 38) do (
    if exist "C:\Python%%v\python.exe" (
        echo [FOUND] C:\Python%%v\python.exe
        set "found_paths=1"
    )
)

if "%found_paths%"=="" (
    echo [NONE] No Python found in common installation directories
)
echo.

echo ====================
echo RECOMMENDED: Use 'py' command which was found on your system
echo ====================
echo.
pause
