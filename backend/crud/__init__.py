from backend.crud.crud_user import crud_user
from backend.crud.crud_chat import crud_chat
from backend.crud.crud_file import crud_file

user = crud_user
chat = crud_chat
file = crud_file

__all__ = ["user", "chat", "file"]