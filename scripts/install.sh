#!/bin/bash

# 检查Python版本和conda
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
has_conda=0

if command -v conda &> /dev/null; then
    has_conda=1
fi

# 选择安装方式
echo "请选择安装方式:"
echo "1) 使用Python虚拟环境(venv)"
if [ $has_conda -eq 1 ]; then
    echo "2) 使用Conda环境"
fi
read -r choice

case $choice in
    1)
        if [ "$python_version" != "3.10" ]; then
            echo "错误: 需要Python 3.10版本"
            echo "当前版本: $python_version"
            exit 1
        fi
        echo "创建Python虚拟环境..."
        python3.10 -m venv AI-lawyer
        source AI-lawyer/bin/activate || source AI-lawyer/Scripts/activate
        ;;
    2)
        if [ $has_conda -eq 0 ]; then
            echo "未检测到conda，请先安装Miniconda或Anaconda"
            exit 1
        fi
        echo "创建Conda环境..."
        conda create -n AI-lawyer python=3.10 -y
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate AI-lawyer
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

# 升级pip并安装依赖
echo "升级pip并安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p data/uploads
mkdir -p data/vector_db

echo "安装完成！"
if [ "$choice" = "1" ]; then
    echo "使用 'source AI-lawyer/bin/activate' 或 'source AI-lawyer/Scripts/activate' 激活环境"
else
    echo "使用 'conda activate AI-lawyer' 激活环境"
fi