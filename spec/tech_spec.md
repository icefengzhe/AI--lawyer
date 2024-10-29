# AI Lawyer 技术规格说明

## 1. 系统架构

### 1.1 整体架构
- 前后端分离架构
- RESTful API + WebSocket实时通信
- 基于RAG的智能问答系统

### 1.2 技术栈
#### 1.2.1 后端技术
- Python 3.10
- FastAPI 框架
- SQLAlchemy ORM
- LangChain RAG框架
- ChatTongyi 大语言模型
- FAISS 向量数据库

### 1.3 安全配置
- JWT认证
  - JWT_SECRET_KEY: 用于token的签名和验证
  - JWT_ALGORITHM: HS256
  - JWT_EXPIRE_MINUTES: token有效期（分钟）

### 1.4 环境变量
必需的环境变量：
- JWT_SECRET_KEY: JWT密钥
- DASHSCOPE_API_KEY: AI模型API密钥

可选的环境变量：
- DATABASE_URL: 数据库连接URL
- LOG_LEVEL: 日志级别
- VECTOR_DB_PATH: 向量数据库路径

## 后端技术要求

### 构建后端API服务

- **编程语言**：Python 版本 3.10
- **Rest API 使用**：FastAPI
- **跨域支持**：使用 FastAPI 的 CORS 中间件，允许前端与后端进行跨域通信。

### RAG 应用

- 使用 Langchain 进行大语言模型处理。
- 大语言模型使用`ChatTongyi`,`DASHSCOPE_API_KEY`在`.env`文件中配置。

### 用户聊天

- 进行对话时，按照传统 RAG 的流程切分成小的 chunks，后进行 embedding 后，写入向量数据库。
  - 分块的大小：每个 chunk 的字符数（如 50-100 字符），可以使用 Langchain 的 `CharacterTextSplitter` 方法。
- 历史对话根据用户id存储在数据库中
- 向量数据库使用 Landchain 的向量数据库技术。

### 对话功能

- 支持用户和 AI 的多轮对话，对话历史信息要作为上下文保留在 prompt 中。

### 配置管理

- 将关键配置如数据库路径、模型路径等集中在 `config.py` 文件中。
- 支持通过环境变量进行配置。

## 前端开发技术指南

### 编程语言

- HTML5, CSS3, JavaScript（ES6+）

### 前端框架与工具

- **H5框架**：使用原生HTML5、CSS3和JavaScript进行开发，或者可以选择使用如React Native for Web（如果希望复用React组件）等框架来模拟H5体验，但核心仍基于H5标准。
- **构建工具**：Webpack（用于打包和构建）
- **CSS预处理器**：可以选择使用Sass或Less，但直接使用CSS3也是可行的。

### 前端实时聊天功能

- 实现方式：通过 WebSocket 实现前端与后端的双向通信，确保聊天消息的及时响应。
- WebSocket 断开处理：
  - 当页面的 WebSocket 断开时，需要有相关的提示信息。
  - 需要能够重新连接，并在连接成功后将出错信息消除。


### 后端依赖

- 所有后端的依赖项应写入 `requirements.txt` 文件。
- 确保这些依赖的版本和 Python 的版本都要兼容。
- 一些已知的 Python 依赖（与之前相同）：

```
langchain
langchain-community
langchain-core
langchain-text-splitters
fastapi
faiss-cpu
ollama
langchain-ollama
uvicorn
python-multipart
pypdf
pydantic
python-dotenv
websockets
```

### 前端依赖

- 由于使用原生H5开发，主要依赖为构建工具和可能的第三方库（如WebSocket库）。


## 编码规范指南


### 通用规范

- 在项目根目录下生成`.gitignore`文件，确保排除以下目录，以避免提交不必要的依赖和编译文件：
  - `node_modules/`（如果使用Node.js工具链）
  - `dist/`
  - `__pycache__/`
  - `env/`

### 前端代码规范

前端代码存放在项目根目录下的`frontend`目录中（如果使用独立前端目录结构）。


### 后端代码规范

后端代码存放在项目根目录下的`backend`目录中。


## 日志

- **日志级别**：设置为INFO级别。
- **日志输出**：在合适的部分增加必要的输出到控制台，方便理解和调试代码。并且可以根据需要进一步配置输出到日志文件。
- **日志内容**：记录所有关键流程，例如向量生成、查询请求、prompt内容的生成、模型响应等信息。

## 文档

### README

包含程序的简介、使用方法、安装步骤、运行命令以及相关示例。

- **项目介绍**：简要介绍项目的功能和目标。
- **使用说明**：包括如何进行聊天、如何查询历史对话等。
- **安装步骤**：详细描述如何安装依赖项、配置环境、运行后端和前端服务（注意前端部分将基于H5开发，可能不需要Node.js环境，但构建工具链可能需要）。
- **目录结构**：清晰列出前后端目录结构，帮助开发者快速理解代码组织方式。

**注意**：生成两份README文件，`readme.md`放英文版，`readme-cn.md`放中文版。

### 其他文档

在根目录下创建`docs`目录，用于存放其他相关文档。当相关API的交互以及架构发生变化时，请记得更新以下
文档：

- `/docs/api-docs.md`：API交互文档
- `/docs/architecture.md`：项目架构文档
请确保所有文档都保持最新，并易于理解和查找。
