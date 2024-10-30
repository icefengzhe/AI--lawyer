# AI-Lawyer 智能法律助手

基于通义千问大语言模型的智能法律咨询助手系统。

## 功能特点

- 智能对话：基于通义千问大语言模型的法律咨询对话
- 文档处理：支持上传和分析法律文档（PDF、Word、TXT等）
- 向量检索：基于文档内容的智能检索和问答
- 用户管理：支持多用户系统，数据隔离
- 实时对话：基于WebSocket的流式对话响应

## 技术栈

### 后端
- FastAPI：高性能的Python Web框架
- LangChain：大语言模型应用框架
- ChromaDB：向量数据库
- SQLAlchemy：ORM框架
- JWT：用户认证
- WebSocket：实时通信

### 前端
- HTML + JavaScript
- Element Plus：UI组件库
- Axios：HTTP客户端
- Markdown-it：Markdown渲染

## 项目结构

AI-lawyer/
├── backend/
│   ├── api/                # API路由
│   │   ├── v1/            # API版本1
│   │   │   ├── auth.py    # 认证相关路由
│   │   │   ├── chat.py    # 聊天相关路由
│   │   │   └── file.py    # 文件相关路由
│   │   ├── deps.py        # 依赖项
│   │   ├── file.py        # 文件处理
│   │   └── router.py      # 路由注册
│   ├── services/          # 业务逻辑
│   │   ├── chat.py        # 聊天服务
│   │   ├── file.py        # 文件服务
│   │   └── vector_store.py # 向量存储服务
│   ├── tools/             # 工具函数
│   │   └── file_tools.py  # 文件处理工具
│   └── main.py            # 入口文件
├── frontend/
│   ├── index.html         # 主页面
│   ├── login.html         # 登录页面
│   └── upload.html        # 文件上传页面
├── data/                  # 数据目录
│   ├── uploads/          # 上传文件存储
│   └── vector_db/        # 向量数据库存储
├── requirements.txt      # Python依赖
└── start.sh             # 启动脚本

## API文档

### 认证接口
- POST /api/v1/register - 用户注册
- POST /api/v1/token - 用户登录（获取JWT令牌）

### 聊天接口
- POST /api/v1/chat/send - 发送消息
- GET /api/v1/chat/history - 获取聊天历史
- WebSocket /api/v1/chat/ws/{client_id} - 实时对话

### 文件接口
- POST /api/v1/files/upload - 上传文件
- GET /api/v1/files/list - 获取文件列表
- DELETE /api/v1/files/{file_id} - 删除文件

## 快速开始

### 环境要求
- Python 3.10+
- 通义千问API密钥

### 安装步骤

1. 克隆项目并进入目录
2. 安装后端依赖：
```bash
pip install -r requirements.txt
```

## 部署指南

### 方式一：Docker部署（推荐）

1. 安装Docker和Docker Compose
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# CentOS
sudo yum install docker docker-compose
```

2. 克隆项目
```bash
git clone https://github.com/yourusername/ai-lawyer.git
cd ai-lawyer
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入必要的配置信息，尤其是DASHSCOPE_API_KEY
```

4. 构建和启动容器
```bash
docker-compose up -d
```

### 方式二：手动部署

1. 系统要求
- Python 3.8+
- 通义千问API密钥

2. 安装依赖
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入必要的配置信息
```

4. 启动服务
```bash
chmod +x start.sh
./start.sh
```

## 安全建议

1. 修改默认的JWT密钥
2. 启用HTTPS
3. 定期更新依赖包
4. 配置防火墙规则
5. 启用日志监控

## 常见问题

Q: 如何获取通义千问API密钥？
A: 访问[通义千问开放平台](https://dashscope.aliyun.com/)注册账号并创建API密钥。

Q: 如何备份数据？
A: 定期备份SQLite数据库文件（ai_lawyer.db）。

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request！

## 联系方式

- 邮箱：862628057@qq.com
- GitHub：(https://github.com/icefengzhe)

