@echo off
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE="

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
echo 错误：未找到 Python！
echo 请安装 Python 3.8 或更高版本，或将绿色版 Python 放在
echo %SCRIPT_DIR%python\ 目录下（python.exe 位于该目录内）。
echo 下载地址：https://www.python.org/downloads/
echo ============================================================
pause
exit /b 1

:found
echo 检测到 Python: !PYTHON_EXE!
echo 正在创建虚拟环境（.venv）...
"!PYTHON_EXE!" -m venv ".venv"
if errorlevel 1 (
    echo 创建虚拟环境失败，请检查 Python 版本（需 3.8+）。
    pause
    exit /b 1
)

echo 正在安装依赖（请稍候）...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if exist "%SCRIPT_DIR%requirements.txt" (
    python -m pip install -r requirements.txt
) else (
    echo requirements.txt 不存在，正在安装常用依赖...
    python -m pip install flask flask-cors requests vdf legendary-gl gogdl
)
if errorlevel 1 (
    echo 依赖安装失败，请检查网络或手动安装。
    pause
    exit /b 1
)

echo 正在生成启动脚本 run.bat ...
(
echo @echo off
echo call "%~dp0.venv\Scripts\activate.bat"
echo python app.py
) > "%SCRIPT_DIR%run.bat"

echo ============================================================
echo 安装完成！
echo 运行 run.bat 即可启动 Gamepedia。
echo 如果启动报错，请检查 requirements.txt 中是否包含所有依赖。
echo ============================================================
pause