# AI 律师

AI 律师是一个基于网络的应用程序,通过聊天界面提供快速的法律咨询和建议。它使用检索增强生成(RAG)模型来提供准确和上下文感知的回答。

## 功能特点

- 用户注册和登录
- 法律咨询聊天界面
- 过往对话历史
- 自动生成聊天标题
- 对话反馈系统
- 聊天内容搜索
- 分页加载聊天消息

## 技术栈

### 后端
- Python 3.10
- FastAPI
- SQLAlchemy
- Langchain
- ChatTongyi (通义AI模型)
- FAISS (向量存储)

### 前端
- HTML5
- CSS3
- JavaScript (ES6+)
- WebSocket (实时通信)

## 设置和安装

1. 克隆仓库:
   ```
   git clone https://github.com/yourusername/ai-lawyer.git
   cd ai-lawyer
   ```

2. 设置虚拟环境:
   ```
   python -m venv env
   source env/bin/activate  # Windows下使用 `env\Scripts\activate`
   ```

3. 安装所需包:
   ```
   pip install -r requirements.txt
   ```

4. 设置环境变量:
   在根目录创建一个 `.env` 文件并添加以下内容:
   ```
   DASHSCOPE_API_KEY=你的API密钥
   DATABASE_URL=sqlite:///./test.db
   SECRET_KEY=你的密钥
   VECTOR_DB_PATH=./vector_db
   ```

5. 初始化数据库:
   ```
   python init_db.py
   ```

6. 运行后端服务器:
   ```
   uvicorn app.main:app --reload
   ```

7. 在网络浏览器中打开 `frontend/login.html` 来使用应用程序。

## 使用方法

1. 在登录页面注册新账户或登录现有账户。
2. 在主界面的聊天窗口输入您的法律问题,开始新的对话。
3. 在左侧栏查看您的对话历史,点击可以切换不同的对话。
4. 使用搜索功能查找特定的聊天内容。
5. 如有需要,对AI的回答提供反馈。

## 项目结构

```
ai-lawyer/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── main.py
│   │   ├── config.py
│   │   └── database.py
│   └── requirements.txt
├── frontend/
│   ├── css/
│   ├── js/
│   ├── index.html
│   └── login.html
├── .env
├── .gitignore
├── README.md
└── README-cn.md
```

## 贡献

欢迎贡献!请随时提交Pull Request或开Issue讨论新功能和改进。

## 许可证

本项目采用MIT许可证。
