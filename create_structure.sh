#!/bin/bash

# 创建主目录结构
mkdir -p backend/{api/v1,core,crud,db,models,schemas,services}
mkdir -p frontend/{css,js/api}
mkdir -p logs

# 创建后端文件
touch backend/__init__.py
touch backend/main.py
touch backend/api/__init__.py
touch backend/api/v1/__init__.py
touch backend/api/v1/auth.py
touch backend/api/v1/chat.py
touch backend/core/__init__.py
touch backend/core/config.py
touch backend/core/logger.py
touch backend/crud/__init__.py
touch backend/crud/base.py
touch backend/crud/crud_user.py
touch backend/crud/crud_chat.py
touch backend/db/__init__.py
touch backend/db/base.py
touch backend/db/base_class.py
touch backend/db/database.py
touch backend/models/__init__.py
touch backend/models/user.py
touch backend/models/chat.py
touch backend/schemas/__init__.py
touch backend/schemas/user.py
touch backend/schemas/chat.py
touch backend/schemas/token.py
touch backend/services/__init__.py
touch backend/services/chat.py

# 创建前端文件
touch frontend/index.html
touch frontend/login.html
touch frontend/register.html
touch frontend/css/style.css
touch frontend/css/auth.css
touch frontend/js/main.js
touch frontend/js/auth.js
touch frontend/js/chat.js
touch frontend/js/api/chat.js

# 创建配置文件
touch .env.example
touch requirements.txt
touch README.md
touch README-cn.md

# 创建启动脚本
touch start.sh
chmod +x start.sh

echo "项目结构创建完成！"