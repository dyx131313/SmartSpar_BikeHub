"""
WebSocket路由处理
"""
import asyncio
import websockets
import json
from flask import current_app
from functools import wraps
from app.utils.auth import verify_token
from app.services.websocket_service import ChatWebSocketHandler, websocket_manager
import logging

logger = logging.getLogger(__name__)

def websocket_auth_required(f):
    """WebSocket认证装饰器"""
    @wraps(f)
    async def wrapper(websocket, path):
        try:
            # 获取查询参数中的token
            query_params = websockets.parse_uri(path)
            if not query_params:
                await websocket.close(code=4001, reason="缺少认证参数")
                return

            # 从查询参数中获取token
            token = None
            if '?' in query_params:
                params = query_params.split('?')[1]
                param_pairs = params.split('&')
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        if key == 'token':
                            token = value
                            break

            if not token:
                await websocket.close(code=4001, reason="缺少认证令牌")
                return

            # 验证token
            user_data = verify_token(token)
            if not user_data:
                await websocket.close(code=4001, reason="无效的认证令牌")
                return

            user_id = user_data.get('sub') or user_data.get('user_id')
            if not user_id:
                await websocket.close(code=4001, reason="无效的用户信息")
                return

            # 调用处理函数
            await f(websocket, path, user_id)

        except Exception as e:
            logger.error(f"WebSocket认证错误: {e}")
            await websocket.close(code=4001, reason="认证失败")

    return wrapper

async def handle_websocket_connection(websocket, path, user_id):
    """处理WebSocket连接"""
    handler = ChatWebSocketHandler(websocket, path, user_id)
    await handler.handle_connection()

class WebSocketServer:
    """WebSocket服务器"""

    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.server = None

    async def start_server(self):
        """启动WebSocket服务器"""
        try:
            logger.info(f"启动WebSocket服务器 ws://{self.host}:{self.port}")

            self.server = await websockets.serve(
                websocket_auth_required(handle_websocket_connection),
                self.host,
                self.port,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=1,
                max_size=10 * 1024 * 1024,  # 10MB
                compression=None,  # 禁用压缩以提高性能
            )

            logger.info(f"WebSocket服务器已启动在 ws://{self.host}:{self.port}")

        except Exception as e:
            logger.error(f"启动WebSocket服务器失败: {e}")
            raise

    async def stop_server(self):
        """停止WebSocket服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket服务器已停止")

    def run(self):
        """运行WebSocket服务器"""
        try:
            # 设置事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 启动服务器
            loop.run_until_complete(self.start_server())

            # 保持运行
            loop.run_forever()

        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止WebSocket服务器...")
            loop.run_until_complete(self.stop_server())
        except Exception as e:
            logger.error(f"WebSocket服务器运行错误: {e}")
        finally:
            loop.close()

# 全局WebSocket服务器实例
websocket_server = WebSocketServer()

def run_websocket_server():
    """运行WebSocket服务器（用于独立启动）"""
    websocket_server.run()

# WebSocket事件处理
class WebSocketEventHandler:
    """WebSocket事件处理器"""

    @staticmethod
    async def on_user_connected(user_id: int, connection_id: str):
        """用户连接事件"""
        logger.info(f"用户 {user_id} 已连接，连接ID: {connection_id}")

        # 通知其他用户用户上线
        from app.services.websocket_service import message_broadcast

        await message_broadcast.broadcast_user_status_changed(
            user_id, 'online'
        )

    @staticmethod
    async def on_user_disconnected(user_id: int, connection_id: str):
        """用户断开连接事件"""
        logger.info(f"用户 {user_id} 已断开连接，连接ID: {connection_id}")

        # 检查用户是否还有其他连接
        remaining_connections = len(websocket_manager.user_connections.get(user_id, {}))

        if remaining_connections == 0:
            # 用户完全离线，通知其他用户
            from app.services.websocket_service import message_broadcast

            await message_broadcast.broadcast_user_status_changed(
                user_id, 'offline'
            )

    @staticmethod
    async def on_group_message_sent(message_data: dict):
        """群聊消息发送事件"""
        from app.services.websocket_service import message_broadcast

        await message_broadcast.broadcast_new_message(message_data)

    @staticmethod
    async def on_group_message_edited(message_data: dict):
        """群聊消息编辑事件"""
        from app.services.websocket_service import message_broadcast

        await message_broadcast.broadcast_message_edited(message_data)

    @staticmethod
    async def on_group_message_deleted(message_data: dict):
        """群聊消息删除事件"""
        from app.services.websocket_service import message_broadcast

        await message_broadcast.broadcast_message_deleted(message_data)

    @staticmethod
    async def on_group_member_added(group_id: int, member_data: dict):
        """群聊成员添加事件"""
        from app.services.websocket_service import message_broadcast

        await message_broadcast.broadcast_group_member_joined(group_id, member_data)

    @staticmethod
    async def on_group_member_removed(group_id: int, user_id: int):
        """群聊成员移除事件"""
        from app.services.websocket_service import message_broadcast

        await message_broadcast.broadcast_group_member_left(group_id, user_id)

    @staticmethod
    async def on_group_updated(group_data: dict):
        """群聊信息更新事件"""
        from app.services.websocket_service import message_broadcast

        await message_broadcast.broadcast_group_updated(group_data)

# Flask路由中触发WebSocket事件的辅助函数
class WebSocketEventTrigger:
    """WebSocket事件触发器"""

    @staticmethod
    def trigger_message_sent(message_data: dict):
        """触发消息发送事件"""
        asyncio.create_task(
            WebSocketEventHandler.on_group_message_sent(message_data)
        )

    @staticmethod
    def trigger_message_edited(message_data: dict):
        """触发消息编辑事件"""
        asyncio.create_task(
            WebSocketEventHandler.on_group_message_edited(message_data)
        )

    @staticmethod
    def trigger_message_deleted(message_data: dict):
        """触发消息删除事件"""
        asyncio.create_task(
            WebSocketEventHandler.on_group_message_deleted(message_data)
        )

    @staticmethod
    def trigger_member_added(group_id: int, member_data: dict):
        """触发成员添加事件"""
        asyncio.create_task(
            WebSocketEventHandler.on_group_member_added(group_id, member_data)
        )

    @staticmethod
    def trigger_member_removed(group_id: int, user_id: int):
        """触发成员移除事件"""
        asyncio.create_task(
            WebSocketEventHandler.on_group_member_removed(group_id, user_id)
        )

    @staticmethod
    def trigger_group_updated(group_data: dict):
        """触发群聊更新事件"""
        asyncio.create_task(
            WebSocketEventHandler.on_group_updated(group_data)
        )

# 全局事件触发器
websocket_event_trigger = WebSocketEventTrigger()