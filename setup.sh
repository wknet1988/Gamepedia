#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXE=""
LANG="zh"

# 选择语言
echo "============================================================"
echo "请选择语言 / Select Language:"
echo "[1] 中文 (Chinese)"
echo "[2] English"
echo "============================================================"
read -p "请输入数字 / Enter number (1 or 2): " lang_choice
if [ "$lang_choice" = "2" ]; then
    LANG="en"
fi
echo ""

# 定义中英文消息
if [ "$LANG" = "zh" ]; then
    MSG_FIND_PYTHON="检测到 Python: "
    MSG_CREATE_VENV="正在创建虚拟环境（.venv）..."
    MSG_VENV_FAIL="创建虚拟环境失败，请检查 Python 版本（需 3.8+）。"
    MSG_INSTALL_DEPS="正在安装依赖（请稍候）..."
    MSG_PIP_UPGRADE="正在升级 pip..."
    MSG_INSTALL_PIP="正在安装常用依赖..."
    MSG_DEPS_FAIL="依赖安装失败，请检查网络或手动安装。"
    MSG_GEN_RUN="正在生成启动脚本 run.sh ..."
    MSG_DONE="安装完成！运行 ./run.sh 即可启动 Gamepedia。"
    MSG_ERROR_PYTHON="错误：未找到 Python！请安装 Python 3.8+，或将绿色版 Python 放在 ${SCRIPT_DIR}/python/ 目录下（python 可执行文件位于该目录内）。下载地址：https://www.python.org/downloads/"
    MSG_CHECK_VENV="检查虚拟环境是否存在..."
    MSG_RUN_SCRIPT="运行 ./run.sh 启动程序。"
else
    MSG_FIND_PYTHON="Found Python: "
    MSG_CREATE_VENV="Creating virtual environment (.venv)..."
    MSG_VENV_FAIL="Failed to create virtual environment. Please ensure Python 3.8+ is installed."
    MSG_INSTALL_DEPS="Installing dependencies (please wait)..."
    MSG_PIP_UPGRADE="Upgrading pip..."
    MSG_INSTALL_PIP="Installing common dependencies..."
    MSG_DEPS_FAIL="Dependency installation failed. Please check network or install manually."
    MSG_GEN_RUN="Generating run.sh startup script..."
    MSG_DONE="Installation complete! Run ./run.sh to start Gamepedia."
    MSG_ERROR_PYTHON="Error: Python not found! Please install Python 3.8+, or place a portable Python in ${SCRIPT_DIR}/python/ (with python executable inside). Download: https://www.python.org/downloads/"
    MSG_CHECK_VENV="Checking if virtual environment exists..."
    MSG_RUN_SCRIPT="Run ./run.sh to launch the application."
fi

# 1. 检查当前目录下的 python 子目录（绿色版）
if [ -x "${SCRIPT_DIR}/python/bin/python3" ]; then
    PYTHON_EXE="${SCRIPT_DIR}/python/bin/python3"
elif [ -x "${SCRIPT_DIR}/python/python" ]; then
    PYTHON_EXE="${SCRIPT_DIR}/python/python"
fi

if [ -n "$PYTHON_EXE" ]; then
    echo "${MSG_FIND_PYTHON}${PYTHON_EXE}"
else
    # 2. 检查系统 PATH 中的 python3
    if command -v python3 &> /dev/null; then
        PYTHON_EXE="python3"
    elif command -v python &> /dev/null; then
        PYTHON_EXE="python"
    else
        echo "============================================================"
        echo "$MSG_ERROR_PYTHON"
        echo "============================================================"
        exit 1
    fi
    echo "${MSG_FIND_PYTHON}${PYTHON_EXE}"
fi

echo "$MSG_CREATE_VENV"
"$PYTHON_EXE" -m venv ".venv"
if [ $? -ne 0 ]; then
    echo "$MSG_VENV_FAIL"
    exit 1
fi

echo "$MSG_INSTALL_DEPS"
source ".venv/bin/activate"
echo "$MSG_PIP_UPGRADE"
python -m pip install --upgrade pip
if [ -f "${SCRIPT_DIR}/requirements.txt" ]; then
    python -m pip install -r requirements.txt
else
    echo "$MSG_INSTALL_PIP"
    python -m pip install flask flask-cors requests vdf legendary-gl gogdl
fi
if [ $? -ne 0 ]; then
    echo "$MSG_DEPS_FAIL"
    exit 1
fi

echo "$MSG_GEN_RUN"
cat > "${SCRIPT_DIR}/run.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f "${SCRIPT_DIR}/.venv/bin/activate" ]; then
    echo "============================================================"
    echo "Error: Virtual environment not found!"
    echo "Please run setup.sh first to install."
    echo "============================================================"
    exit 1
fi
source "${SCRIPT_DIR}/.venv/bin/activate"
python app.py
if [ $? -ne 0 ]; then
    echo "============================================================"
    echo "Program exited with error. Check above messages."
    echo "============================================================"
fi
EOF
chmod +x "${SCRIPT_DIR}/run.sh"

echo "============================================================"
echo "$MSG_DONE"
echo "$MSG_RUN_SCRIPT"
echo "============================================================"