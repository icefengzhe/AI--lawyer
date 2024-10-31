#!/bin/bash

# 检查Python版本
required_version="3.10"
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "Error: Python $required_version or higher is required"
    echo "Current version: $python_version"
    exit 1
fi

# 检查并创建.env文件
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

# 创建必要的目录
echo "Creating required directories..."
mkdir -p data/uploads
mkdir -p data/vector_db

# 设置文件权限
echo "Setting file permissions..."
chmod +x scripts/*.sh
chmod 755 data/uploads
chmod 755 data/vector_db

echo "Environment setup completed!" 