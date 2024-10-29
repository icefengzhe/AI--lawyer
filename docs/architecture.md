# AI Lawyer 系统架构文档

## 整体架构

AI Lawyer采用前后端分离的架构设计，主要包含以下组件：

### 前端架构
- 原生JavaScript实现
- 基于WebSocket的实时通信
- JWT认证机制

### 后端架构
- FastAPI框架
- SQLite数据库
- JWT认证服务
- RAG智能问答系统（开发中）

## 核心模块

### 1. 用户认证模块
- JWT token生成和验证
- 密码加密存储
- 会话管理

### 2. 数据库设计
#### 用户表(users)
- id: 主键
- username: 用户名
- email: 邮箱
- hashed_password: 加密密码
- created_at: 创建时间
- updated_at: 更新时间

## 安全设计

### 1. 认证安全
- 使用bcrypt进行密码加密
- JWT token有效期控制
- 密码强度验证

### 2. 通信安全
- HTTPS加密传输
- WebSocket安全连接
- CORS策略控制

## 部署架构

### 开发环境
- 本地SQLite数据库
- 本地文件系统存储
- uvicorn开发服务器

### 生产环境（计划）
- 使用Nginx作为反向代理
- 使用gunicorn作为WSGI服务器
- 数据库迁移至PostgreSQL