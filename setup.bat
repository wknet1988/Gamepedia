@echo off
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE="
set "LANG=zh"

:: 选择语言 / Select Language
echo ============================================================
echo 请选择语言 / Select Language:
echo [1] 中文 (Chinese)
echo [2] English
echo ============================================================
choice /C 12 /N /M "请输入数字 / Enter number (1 or 2): "
if errorlevel 2 (set "LANG=en") else (set "LANG=zh")
echo.

:: 定义中英文提示
if "%LANG%"=="zh" (
    set "MSG_FIND_PYTHON=检测到 Python: !PYTHON_EXE!"
    set "MSG_CREATE_VENV=正在创建虚拟环境（.venv）..."
    set "MSG_VENV_FAIL=创建虚拟环境失败，请检查 Python 版本（需 3.8+）。"
    set "MSG_INSTALL_DEPS=正在安装依赖（请稍候）..."
    set "MSG_PIP_UPGRADE=正在升级 pip..."
    set "MSG_INSTALL_PIP=正在安装常用依赖..."
    set "MSG_DEPS_FAIL=依赖安装失败，请检查网络或手动安装。"
    set "MSG_GEN_RUN=正在生成启动脚本 run.bat ..."
    set "MSG_DONE=安装完成！运行 run.bat 即可启动 Gamepedia。"
    set "MSG_ERROR_PYTHON=错误：未找到 Python！请安装 Python 3.8+，或将绿色版 Python 放在 %SCRIPT_DIR%python\ 目录下。下载地址：https://www.python.org/downloads/"
    set "MSG_CHECK_VENV=检查虚拟环境是否存在..."
    set "MSG_RUN_SCRIPT=运行 run.bat 启动程序。"
) else (
    set "MSG_FIND_PYTHON=Found Python: !PYTHON_EXE!"
    set "MSG_CREATE_VENV=Creating virtual environment (.venv)..."
    set "MSG_VENV_FAIL=Failed to create virtual environment. Please ensure Python 3.8+ is installed."
    set "MSG_INSTALL_DEPS=Installing dependencies (please wait)..."
    set "MSG_PIP_UPGRADE=Upgrading pip..."
    set "MSG_INSTALL_PIP=Installing common dependencies..."
    set "MSG_DEPS_FAIL=Dependency installation failed. Please check network or install manually."
    set "MSG_GEN_RUN=Generating run.bat startup script..."
    set "MSG_DONE=Installation complete! Run run.bat to start Gamepedia."
    set "MSG_ERROR_PYTHON=Error: Python not found! Please install Python 3.8+, or place a portable Python in %SCRIPT_DIR%python\ (python.exe inside). Download: https://www.python.org/downloads/"
    set "MSG_CHECK_VENV=Checking if virtual environment exists..."
    set "MSG_RUN_SCRIPT=Run run.bat to launch the application."
)

:: 1. 检查当前目录下的 python 子目录（绿色版）
if exist "%SCRIPT_DIR%python\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%python\python.exe"
    goto :found
)

:: 2. 检查系统 PATH 中的 python
where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=python"
    goto :found
)

:: 3. 检查 py 启动器（Python 3）
where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_EXE=py -3"
    goto :found
)

:: 未找到 Python
echo ============================================================
echo %MSG_ERROR_PYTHON%
echo ============================================================
pause
exit /b 1

:found
echo %MSG_FIND_PYTHON%
echo %MSG_CREATE_VENV%
"!PYTHON_EXE!" -m venv ".venv"
if errorlevel 1 (
    echo %MSG_VENV_FAIL%
    pause
    exit /b 1
)

echo %MSG_INSTALL_DEPS%
call ".venv\Scripts\activate.bat"
echo %MSG_PIP_UPGRADE%
python -m pip install --upgrade pip
if exist "%SCRIPT_DIR%requirements.txt" (
    python -m pip install -r requirements.txt
) else (
    echo %MSG_INSTALL_PIP%
    python -m pip install flask flask-cors requests vdf legendary-gl gogdl
)
if errorlevel 1 (
    echo %MSG_DEPS_FAIL%
    pause
    exit /b 1
)

echo %MSG_GEN_RUN%
(
echo @echo off
echo set "SCRIPT_DIR=%%~dp0"
echo if not exist "%%SCRIPT_DIR%%.venv\Scripts\activate.bat" (
echo     echo ============================================================
echo     echo Error: Virtual environment not found!
echo     echo Please run setup.bat first to install.
echo     echo ============================================================
echo     pause
echo     exit /b 1
echo )
echo call "%%SCRIPT_DIR%%.venv\Scripts\activate.bat"
echo python app.py
echo if errorlevel 1 (
echo     echo ============================================================
echo     echo Program exited with error. Check above messages.
echo     echo ============================================================
echo     pause
echo )
) > "%SCRIPT_DIR%run.bat"

echo ============================================================
echo %MSG_DONE%
echo %MSG_RUN_SCRIPT%
echo ============================================================
pause