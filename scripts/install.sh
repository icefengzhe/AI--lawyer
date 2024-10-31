#!/bin/bash

# 严格检查 Python 3.10 版本
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

if [ "$python_version" != "3.10" ]; then
    echo "Error: This project requires Python 3.10 exactly"
    echo "Current version: $python_version"
    echo "Please install Python 3.10 and try again"
    exit 1
fi

# 创建虚拟环境
echo "Creating virtual environment with Python 3.10..."
python3.10 -m venv venv

# 激活虚拟环境
source venv/bin/activate || source venv/Scripts/activate

# 升级pip并安装依赖
echo "Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
echo "Creating required directories..."
mkdir -p data/uploads
mkdir -p data/vector_db

echo "Installation completed successfully!" 