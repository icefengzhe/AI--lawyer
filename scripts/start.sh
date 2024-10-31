#!/bin/bash

# 设置环境变量
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "安装后端依赖..."
if [ -f /.dockerenv ]; then
    # Docker环境
    echo "Docker环境"
else
    # 本地环境
    if command -v conda &> /dev/null; then
        # Conda环境
        if ! conda env list | grep -q "AI-lawyer"; then
            conda create -n AI-lawyer python=3.10 -y
        fi
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate AI-lawyer
        echo "Conda环境已激活"
    else
        # Python虚拟环境
        if [ ! -d "AI-lawyer" ]; then
            python -m venv AI-lawyer
        fi
        source AI-lawyer/bin/activate || source AI-lawyer/Scripts/activate
        echo "Python虚拟环境已激活"
    fi

fi

pip install --upgrade pip
pip install -r requirements.txt

echo "安装前端依赖..."
# 创建前端依赖目录
mkdir -p frontend/lib

# 下载前端依赖
if [ ! -f "frontend/lib/marked.min.js" ]; then
    echo "下载 marked.min.js..."
    curl -o frontend/lib/marked.min.js https://cdn.jsdelivr.net/npm/marked/marked.min.js
fi

if [ ! -f "frontend/lib/highlight.min.js" ]; then
    echo "下载 highlight.min.js..."
    curl -o frontend/lib/highlight.min.js https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js
fi

if [ ! -f "frontend/lib/highlight.github.css" ]; then
    echo "下载 highlight.github.css..."
    curl -o frontend/lib/highlight.github.css https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css
fi

echo "启动服务..."
if [ -f /.dockerenv ]; then
    # Docker环境启动
    exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
else
    # 本地环境启动（开发模式）
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
fi

# 退出时清理
trap 'echo "服务停止"; exit' INT TERM 