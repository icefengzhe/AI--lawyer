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

# 检查.env文件
if [ ! -f .env ]; then
    echo "创建.env文件..."
    cp .env.example .env
    echo "请修改.env文件中的配置信息"
    exit 1
fi

# 安装后端依赖
echo "安装后端依赖..."
pip install -r requirements.txt

# 安装前端依赖
echo "安装前端依赖..."
cd frontend

# 如果lib目录不存在，下载依赖
if [ ! -d "lib" ] || [ -z "$(ls -A lib)" ]; then
    mkdir -p lib
    echo "下载前端依赖..."
    
    # 使用marked.js替代markdown-it
    curl -L "https://cdn.bootcdn.net/ajax/libs/marked/4.3.0/marked.min.js" -o lib/marked.min.js
    curl -L "https://cdn.bootcdn.net/ajax/libs/highlight.js/11.7.0/highlight.min.js" -o lib/highlight.min.js
    curl -L "https://cdn.bootcdn.net/ajax/libs/highlight.js/11.7.0/styles/github.min.css" -o lib/highlight.github.css
    
    # 如果下载失败，使用备用CDN
    if [ $? -ne 0 ]; then
        echo "使用备用CDN..."
        curl -L "https://lf26-cdn-tos.bytecdntp.com/cdn/expire-1-M/marked/4.3.0/marked.min.js" -o lib/marked.min.js
        curl -L "https://lf26-cdn-tos.bytecdntp.com/cdn/expire-1-M/highlight.js/11.7.0/highlight.min.js" -o lib/highlight.min.js
        curl -L "https://lf26-cdn-tos.bytecdntp.com/cdn/expire-1-M/highlight.js/11.7.0/styles/github.min.css" -o lib/highlight.github.css
    fi
    
    # 如果仍然失败，使用第三个备用CDN
    if [ $? -ne 0 ]; then
        echo "使用第三个备用CDN..."
        curl -L "https://cdn.staticfile.org/marked/4.3.0/marked.min.js" -o lib/marked.min.js
        curl -L "https://cdn.staticfile.org/highlight.js/11.7.0/highlight.min.js" -o lib/highlight.min.js
        curl -L "https://cdn.staticfile.org/highlight.js/11.7.0/styles/github.min.css" -o lib/highlight.github.css
    fi
fi

cd ..

# 创建logs目录
mkdir -p logs

# 启动服务
echo "启动服务..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload