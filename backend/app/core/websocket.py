from fastapi import WebSocket
from typing import List, Dict
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.last_activity: Dict[WebSocket, datetime] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        self.last_activity[websocket] = datetime.utcnow()
        logger.info(f"User {user_id} connected. Active connections: {len(self.active_connections[user_id])}")

    async def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                del self.last_activity[websocket]
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                logger.info(f"User {user_id} disconnected")
            except ValueError:
                pass

    async def send_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                    self.last_activity[connection] = datetime.utcnow()
                except Exception as e:
                    logger.error(f"Error sending message: {str(e)}")
                    disconnected.append(connection)

            # 清理断开的连接
            for connection in disconnected:
                await self.disconnect(connection, user_id)

    async def broadcast(self, message: dict):
        """向所有连接的客户端广播消息"""
        disconnected_users = []
        for user_id in self.active_connections:
            try:
                await self.send_message(message, user_id)
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {str(e)}")
                disconnected_users.append(user_id)

        # 清理断开的用户
        for user_id in disconnected_users:
            if user_id in self.active_connections:
                del self.active_connections[user_id]

    async def check_connections(self):
        """检查并清理不活跃的连接"""
        while True:
            try:
                now = datetime.utcnow()
                for user_id in list(self.active_connections.keys()):
                    for connection in list(self.active_connections[user_id]):
                        if (now - self.last_activity[connection]).seconds > 60:  # 60秒超时
                            await self.disconnect(connection, user_id)
                await asyncio.sleep(30)  # 每30秒检查一次
            except Exception as e:
                logger.error(f"Error checking connections: {str(e)}")
                await asyncio.sleep(5)

    def get_connection_count(self, user_id: int) -> int:
        """获取用户的活跃连接数"""
        return len(self.active_connections.get(user_id, []))

manager = ConnectionManager()

# 启动连接检查任务
@asyncio.create_task
async def start_connection_checker():
    await manager.check_connections()
