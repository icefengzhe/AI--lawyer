## 快速开始

1. 克隆项目
```bash
git clone https://github.com/yourusername/ai-lawyer.git
cd ai-lawyer
```

2. 安装后端依赖
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
npm install
cd ..
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置信息
```

5. 运行项目
```bash
chmod +x start.sh
./start.sh
```

访问 http://localhost:8000 即可使用系统。
