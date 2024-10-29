#!/bin/bash

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "请先安装Python 3"
    exit 1
fi

# 设置Python路径
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 启动服务
echo "启动服务..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload