# AI Lawyer - 智能法律顾问

AI Lawyer 是一个基于大语言模型的智能法律咨询系统，为用户提供专业的法律建议和咨询服务。

## 功能特点

- 智能法律咨询：提供专业、准确的法律建议
- 实时对话：流畅的对话体验，支持实时响应
- 历史记录：保存对话历史，方便随时查看
- 多主题支持：覆盖多个法律领域
- 现代化界面：简洁优雅的用户界面设计

## 技术栈

### 后端
- FastAPI
- SQLAlchemy
- LangChain
- 通义千问大语言模型

### 前端
- 原生JavaScript
- 现代CSS
- Server-Sent Events (SSE)

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/yourusername/ai-lawyer.git
cd ai-lawyer
```

2. 安装依赖
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置信息
```

4. 运行项目
```bash
chmod +x start.sh  # 添加执行权限
./start.sh        # 启动服务
```

访问 http://localhost:8000 即可使用系统。

## 项目结构

```
ai-lawyer/
├── backend/
│   ├── api/          # API路由
│   ├── core/         # 核心配置
│   ├── crud/         # 数据库操作
│   ├── db/           # 数据库配置
│   ├── models/       # 数据模型
│   ├── schemas/      # Pydantic模型
│   └── services/     # 业务逻辑
├── frontend/
│   ├── css/          # 样式文件
│   ├── js/          # JavaScript文件
│   └── index.html   # 主页面
└── logs/            # 日志文件
```

## 环境要求

- Python 3.8+
- Node.js 14+
- 通义千问API密钥

## 配置说明

在 `.env` 文件中配置以下参数：

```env
# API设置
DASHSCOPE_API_KEY=your_api_key

# JWT设置
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# 数据库设置
DATABASE_URL=sqlite:///./ai_lawyer.db

# 日志设置
LOG_LEVEL=INFO
```

## 开发说明

- 后端API遵循RESTful设计规范
- 使用类型提示和文档字符串
- 遵循PEP 8编码规范
- 前端采用模块化设计

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request！

## 联系方式

- 邮箱：862628057@qq.com
- GitHub：[icefengzhe](https://github.com/icefengzhe)
