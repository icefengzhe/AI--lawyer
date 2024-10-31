#!/bin/bash

# 设置备份目录
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据目录
echo "Backing up data directory..."
tar -czf "$BACKUP_DIR/data_$TIMESTAMP.tar.gz" data/

# 备份向量数据库
echo "Backing up vector database..."
tar -czf "$BACKUP_DIR/vector_db_$TIMESTAMP.tar.gz" data/vector_db/

# 保留最近的5个备份
find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +5 -delete

echo "Backup completed: $TIMESTAMP" 