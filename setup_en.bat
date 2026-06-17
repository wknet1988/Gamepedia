@echo off
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE="

:: 1. Check for portable Python in .\python\ directory
if exist "%SCRIPT_DIR%python\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%python\python.exe"
    goto :found
)

:: 2. Check system PATH for python
where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    goto :found
)

:: 3. Check for py launcher (Python 3)
where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=py -3"
    goto :found
)

:: No Python found
echo ============================================================
echo ERROR: Python not found!
echo Please install Python 3.8 or later, or place a portable
echo Python folder in %SCRIPT_DIR%python\ (with python.exe inside).
echo Download: https://www.python.org/downloads/
echo ============================================================
pause
exit /b 1

:found
echo Detected Python: !PYTHON_EXE!
echo Creating virtual environment (.venv)...
"!PYTHON_EXE!" -m venv ".venv"
if errorlevel 1 (
    echo Failed to create virtual environment. Please check Python version (need 3.8+).
    pause
    exit /b 1
)

echo Installing dependencies (this may take a while)...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if exist "%SCRIPT_DIR%requirements.txt" (
    python -m pip install -r requirements.txt
) else (
    echo requirements.txt not found, installing common dependencies...
    python -m pip install flask flask-cors requests vdf legendary-gl gogdl
)
if errorlevel 1 (
    echo Dependency installation failed. Please check your network or install manually.
    pause
    exit /b 1
)

echo Generating startup script run.bat ...
(
echo @echo off
echo call "%~dp0.venv\Scripts\activate.bat"
echo python app.py
) > "%SCRIPT_DIR%run.bat"

echo ============================================================
echo Installation complete!
echo Run run.bat to start Gamepedia.
echo If startup fails, ensure all dependencies are listed in requirements.txt.
echo ============================================================
pause