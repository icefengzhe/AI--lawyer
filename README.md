# AI-Lawyer 智能法律助手

基于通义千问大语言模型的智能法律咨询助手系统。

## 功能特点 ✨

- 🤖 智能对话：基于通义千问大语言模型的法律咨询对话
- 📄 文档处理：支持上传和分析法律文档（PDF、Word、TXT等）
- 🔍 向量检索：基于文档内容的智能检索和问答
- 👥 用户管理：支持多用户系统，数据隔离
- ⚡ 实时对话：基于WebSocket的流式对话响应

## 环境要求 🛠️

### 必需环境
- Python 3.10（强制建议，不建议其他版本）
- Node.js 16+
- 通义千问API密钥

### 可选环境
- Docker & Docker Compose (如需容器化部署)

## 快速开始 🚀

### 本地部署

1. 确保安装了 Python 3.10 或更高版本：
```bash
python --version
```

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

```
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

#### 使用Python虚拟环境

1. 系统要求
- Python 3.10
- 通义千问API密钥

2. 安装依赖
```bash
python -m venv AI-Lawyer
source AI-Lawyer/bin/activate  # Windows: .\AI-Lawyer\Scripts\activate
pip install -r requirements.txt
```
#### 或使用 Conda（推荐）

1. 安装 Miniconda 或 Anaconda

2. 创建并激活 conda 环境
```bash
conda create -n AI-Lawyer python=3.10
conda activate AI-Lawyer
```

配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入必要的配置信息
```

启动服务
```bash
chmod +x scripts/start.sh
./scripts/start.sh
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

