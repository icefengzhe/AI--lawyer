import logging
import sys
from pathlib import Path
from backend.core.config import settings

# 创建logs目录
LOG_PATH = Path("logs")
LOG_PATH.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_PATH / "ai_lawyer.log"

# 配置日志格式
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# 创建logger实例
logger = logging.getLogger("ai_lawyer")
logger.setLevel(logging.INFO)  # 设置为INFO级别

# 清除现有的处理器
logger.handlers.clear()

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
console_handler.setLevel(logging.INFO)  # 控制台显示INFO及以上级别
logger.addHandler(console_handler)

# 创建文件处理器
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
file_handler.setLevel(logging.DEBUG)  # 文件记录DEBUG及以上级别
logger.addHandler(file_handler)

# 禁用uvicorn的访问日志
uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.disabled = True

# 导出logger实例
__all__ = ["logger"]