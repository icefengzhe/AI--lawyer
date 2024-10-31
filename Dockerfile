FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ backend/
COPY scripts/ scripts/

# 设置权限
RUN chmod +x scripts/start.sh

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["scripts/start.sh"] 