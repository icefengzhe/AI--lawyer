from typing import TYPE_CHECKING

__all__ = ["User", "Chat", "Message", "File"]

# 直接导出模型，但使用延迟导入避免循环引用
def get_user():
    from .user import User
    return User

def get_chat_models():
    from .chat import Chat, Message
    return Chat, Message

def get_file():
    from .file import File
    return File

# 实际导出模型
User = get_user()
Chat, Message = get_chat_models()
File = get_file()