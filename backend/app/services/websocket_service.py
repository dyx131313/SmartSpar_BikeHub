"""
WebSocket服务，用于实时消息推送
"""
import json
import asyncio
from typing import Dict, Set, Any, Optional
from datetime import datetime
from flask import current_app
import websockets
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储用户连接 {user_id: {connection_id: websocket}}
        self.user_connections: Dict[int, Dict[str, Any]] = {}
        # 存储群聊连接 {group_id: {user_id: [connection_id]}}
        self.group_connections: Dict[int, Dict[int, Set[str]]] = {}
        # 连接计数器
        self.connection_counter = 0

    async def connect_user(self, websocket, user_id: int, group_ids: list = None) -> str:
        """用户连接WebSocket"""
        connection_id = f"conn_{self.connection_counter}"
        self.connection_counter += 1

        # 添加到用户连接
        if user_id not in self.user_connections:
            self.user_connections[user_id] = {}

        self.user_connections[user_id][connection_id] = {
            'websocket': websocket,
            'connected_at': datetime.now(),
            'group_ids': set(group_ids or [])
        }

        # 添加到群聊连接
        if group_ids:
            for group_id in group_ids:
                if group_id not in self.group_connections:
                    self.group_connections[group_id] = {}

                if user_id not in self.group_connections[group_id]:
                    self.group_connections[group_id][user_id] = set()

                self.group_connections[group_id][user_id].add(connection_id)

        logger.info(f"用户 {user_id} 连接WebSocket，连接ID: {connection_id}")
        return connection_id

    async def disconnect_user(self, user_id: int, connection_id: str):
        """用户断开WebSocket连接"""
        # 从用户连接中移除
        if user_id in self.user_connections:
            if connection_id in self.user_connections[user_id]:
                user_info = self.user_connections[user_id][connection_id]
                group_ids = user_info.get('group_ids', set())

                # 从群聊连接中移除
                for group_id in group_ids:
                    if group_id in self.group_connections:
                        if user_id in self.group_connections[group_id]:
                            self.group_connections[group_id][user_id].discard(connection_id)

                            # 如果用户在该群聊没有其他连接，移除用户
                            if not self.group_connections[group_id][user_id]:
                                del self.group_connections[group_id][user_id]

                            # 如果群聊没有用户连接，移除群聊
                            if not self.group_connections[group_id]:
                                del self.group_connections[group_id]

                del self.user_connections[user_id][connection_id]

                # 如果用户没有其他连接，移除用户
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]

        logger.info(f"用户 {user_id} 断开WebSocket连接，连接ID: {connection_id}")

    async def join_group(self, user_id: int, group_id: int, connection_id: str):
        """用户加入群聊"""
        if user_id in self.user_connections and connection_id in self.user_connections[user_id]:
            self.user_connections[user_id][connection_id]['group_ids'].add(group_id)

        if group_id not in self.group_connections:
            self.group_connections[group_id] = {}

        if user_id not in self.group_connections[group_id]:
            self.group_connections[group_id][user_id] = set()

        self.group_connections[group_id][user_id].add(connection_id)

        logger.info(f"用户 {user_id} 加入群聊 {group_id}")

    async def leave_group(self, user_id: int, group_id: int, connection_id: str):
        """用户离开群聊"""
        if user_id in self.user_connections and connection_id in self.user_connections[user_id]:
            self.user_connections[user_id][connection_id]['group_ids'].discard(group_id)

        if group_id in self.group_connections and user_id in self.group_connections[group_id]:
            self.group_connections[group_id][user_id].discard(connection_id)

            if not self.group_connections[group_id][user_id]:
                del self.group_connections[group_id][user_id]

            if not self.group_connections[group_id]:
                del self.group_connections[group_id]

        logger.info(f"用户 {user_id} 离开群聊 {group_id}")

    async def send_to_user(self, user_id: int, message: dict):
        """发送消息给特定用户的所有连接"""
        if user_id not in self.user_connections:
            return

        disconnected_connections = []

        for connection_id, user_info in self.user_connections[user_id].items():
            try:
                websocket = user_info['websocket']
                await websocket.send(json.dumps(message, ensure_ascii=False, default=str))
            except Exception as e:
                logger.error(f"发送消息给用户 {user_id} 连接 {connection_id} 失败: {e}")
                disconnected_connections.append(connection_id)

        # 清理断开的连接
        for connection_id in disconnected_connections:
            await self.disconnect_user(user_id, connection_id)

    async def send_to_group(self, group_id: int, message: dict, exclude_user_id: int = None):
        """发送消息给群聊中的所有用户"""
        if group_id not in self.group_connections:
            return

        disconnected_connections = []

        for user_id, connections in self.group_connections[group_id].items():
            # 排除特定用户
            if exclude_user_id and user_id == exclude_user_id:
                continue

            for connection_id in connections:
                try:
                    if user_id in self.user_connections and connection_id in self.user_connections[user_id]:
                        websocket = self.user_connections[user_id][connection_id]['websocket']
                        await websocket.send(json.dumps(message, ensure_ascii=False, default=str))
                except Exception as e:
                    logger.error(f"发送群聊消息给用户 {user_id} 连接 {connection_id} 失败: {e}")
                    disconnected_connections.append((user_id, connection_id))

        # 清理断开的连接
        for user_id, connection_id in disconnected_connections:
            await self.disconnect_user(user_id, connection_id)

    async def broadcast_to_all(self, message: dict):
        """广播消息给所有连接的用户"""
        disconnected_connections = []

        for user_id, connections in self.user_connections.items():
            for connection_id, user_info in connections.items():
                try:
                    websocket = user_info['websocket']
                    await websocket.send(json.dumps(message, ensure_ascii=False, default=str))
                except Exception as e:
                    logger.error(f"广播消息给用户 {user_id} 连接 {connection_id} 失败: {e}")
                    disconnected_connections.append((user_id, connection_id))

        # 清理断开的连接
        for user_id, connection_id in disconnected_connections:
            await self.disconnect_user(user_id, connection_id)

    def get_online_users_count(self) -> int:
        """获取在线用户数量"""
        return len(self.user_connections)

    def get_group_online_users_count(self, group_id: int) -> int:
        """获取群聊在线用户数量"""
        return len(self.group_connections.get(group_id, {}))

    def get_user_groups(self, user_id: int) -> Set[int]:
        """获取用户加入的群聊"""
        groups = set()
        if user_id in self.user_connections:
            for user_info in self.user_connections[user_id].values():
                groups.update(user_info.get('group_ids', set()))
        return groups

# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()

class ChatWebSocketHandler:
    """聊天WebSocket处理器"""

    def __init__(self, websocket, path: str, user_id: int):
        self.websocket = websocket
        self.path = path
        self.user_id = user_id
        self.connection_id = None
        self.user_groups = set()

    async def handle_connection(self):
        """处理WebSocket连接"""
        try:
            # 获取用户的群聊列表
            self.user_groups = await self.get_user_groups()

            # 连接用户
            self.connection_id = await websocket_manager.connect_user(
                self.websocket, self.user_id, list(self.user_groups)
            )

            # 发送连接成功消息
            await self.send_connection_success()

            # 发送未读消息数量
            await self.send_unread_count()

            # 监听消息
            await self.listen_messages()

        except Exception as e:
            logger.error(f"WebSocket处理错误: {e}")
        finally:
            # 清理连接
            if self.connection_id:
                await websocket_manager.disconnect_user(self.user_id, self.connection_id)

    async def get_user_groups(self) -> set:
        """获取用户加入的群聊"""
        try:
            from app.utils.database import get_db_connection

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT group_id FROM chat_group_members
                WHERE user_id = %s AND is_active = 1
            """, (self.user_id,))

            groups = {row[0] for row in cursor.fetchall()}

            cursor.close()
            conn.close()

            return groups

        except Exception as e:
            logger.error(f"获取用户群聊失败: {e}")
            return set()

    async def send_connection_success(self):
        """发送连接成功消息"""
        message = {
            'type': 'connection_success',
            'data': {
                'user_id': self.user_id,
                'groups': list(self.user_groups),
                'online_count': websocket_manager.get_online_users_count()
            }
        }

        await self.websocket.send(json.dumps(message, ensure_ascii=False, default=str))

    async def send_unread_count(self):
        """发送未读消息数量"""
        try:
            from app.utils.database import get_db_connection

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) as count
                FROM chat_messages cm
                INNER JOIN chat_group_members cgm ON cm.group_id = cgm.group_id
                WHERE cgm.user_id = %s AND cgm.is_active = 1
                AND cm.created_at > COALESCE(cgm.last_read_at, '1970-01-01')
                AND cm.sender_id != %s AND cm.is_deleted = 0
            """, (self.user_id, self.user_id))

            unread_count = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            message = {
                'type': 'unread_count',
                'data': {
                    'count': unread_count
                }
            }

            await self.websocket.send(json.dumps(message, ensure_ascii=False, default=str))

        except Exception as e:
            logger.error(f"获取未读消息数量失败: {e}")

    async def listen_messages(self):
        """监听客户端消息"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(data)
                except json.JSONDecodeError:
                    await self.send_error('无效的JSON格式')
                except Exception as e:
                    logger.error(f"处理客户端消息错误: {e}")
                    await self.send_error('处理消息失败')

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"用户 {self.user_id} WebSocket连接关闭")
        except Exception as e:
            logger.error(f"WebSocket监听错误: {e}")

    async def handle_client_message(self, data: dict):
        """处理客户端消息"""
        message_type = data.get('type')

        if message_type == 'ping':
            await self.send_pong()

        elif message_type == 'join_group':
            group_id = data.get('group_id')
            if group_id:
                await self.handle_join_group(group_id)

        elif message_type == 'leave_group':
            group_id = data.get('group_id')
            if group_id:
                await self.handle_leave_group(group_id)

        elif message_type == 'mark_as_read':
            message_id = data.get('message_id')
            if message_id:
                await self.handle_mark_as_read(message_id)

        elif message_type == 'typing':
            group_id = data.get('group_id')
            is_typing = data.get('is_typing', False)
            if group_id:
                await self.handle_typing(group_id, is_typing)

        else:
            await self.send_error('未知消息类型')

    async def send_pong(self):
        """发送pong响应"""
        message = {
            'type': 'pong',
            'timestamp': datetime.now().isoformat()
        }
        await self.websocket.send(json.dumps(message, ensure_ascii=False, default=str))

    async def handle_join_group(self, group_id: int):
        """处理加入群聊"""
        if self.connection_id:
            await websocket_manager.join_group(self.user_id, group_id, self.connection_id)
            self.user_groups.add(group_id)

        message = {
            'type': 'group_joined',
            'data': {
                'group_id': group_id,
                'user_id': self.user_id
            }
        }
        await self.websocket.send(json.dumps(message, ensure_ascii=False, default=str))

    async def handle_leave_group(self, group_id: int):
        """处理离开群聊"""
        if self.connection_id:
            await websocket_manager.leave_group(self.user_id, group_id, self.connection_id)
            self.user_groups.discard(group_id)

        message = {
            'type': 'group_left',
            'data': {
                'group_id': group_id,
                'user_id': self.user_id
            }
        }
        await self.websocket.send(json.dumps(message, ensure_ascii=False, default=str))

    async def handle_mark_as_read(self, message_id: int):
        """处理标记消息为已读"""
        try:
            from app.utils.database import get_db_connection

            conn = get_db_connection()
            cursor = conn.cursor()

            # 插入阅读记录
            cursor.execute("""
                INSERT INTO chat_message_reads (message_id, user_id, read_at)
                VALUES (%s, %s, NOW())
                ON DUPLICATE KEY UPDATE read_at = NOW()
            """, (message_id, self.user_id))

            conn.commit()
            cursor.close()
            conn.close()

            message = {
                'type': 'message_marked_read',
                'data': {
                    'message_id': message_id,
                    'user_id': self.user_id
                }
            }
            await self.websocket.send(json.dumps(message, ensure_ascii=False, default=str))

        except Exception as e:
            logger.error(f"标记消息已读失败: {e}")
            await self.send_error('标记消息已读失败')

    async def handle_typing(self, group_id: int, is_typing: bool):
        """处理正在输入状态"""
        if group_id not in self.user_groups:
            await self.send_error('您不是该群聊的成员')
            return

        # 发送给群聊其他用户
        message = {
            'type': 'user_typing',
            'data': {
                'group_id': group_id,
                'user_id': self.user_id,
                'is_typing': is_typing
            }
        }

        await websocket_manager.send_to_group(
            group_id, message, exclude_user_id=self.user_id
        )

    async def send_error(self, error_message: str):
        """发送错误消息"""
        message = {
            'type': 'error',
            'data': {
                'message': error_message
            }
        }
        await self.websocket.send(json.dumps(message, ensure_ascii=False, default=str))

# 消息发送服务
class MessageBroadcastService:
    """消息广播服务"""

    @staticmethod
    async def broadcast_new_message(message_data: dict):
        """广播新消息"""
        group_id = message_data.get('group_id')
        sender_id = message_data.get('sender_id')

        # 构建广播消息
        broadcast_message = {
            'type': 'new_message',
            'data': message_data
        }

        # 发送给群聊成员
        await websocket_manager.send_to_group(
            group_id, broadcast_message, exclude_user_id=sender_id
        )

        # 更新群聊最后消息时间
        await MessageBroadcastService.update_group_last_message(group_id)

    @staticmethod
    async def broadcast_message_edited(message_data: dict):
        """广播消息编辑"""
        group_id = message_data.get('group_id')

        broadcast_message = {
            'type': 'message_edited',
            'data': message_data
        }

        await websocket_manager.send_to_group(group_id, broadcast_message)

    @staticmethod
    async def broadcast_message_deleted(message_data: dict):
        """广播消息删除"""
        group_id = message_data.get('group_id')

        broadcast_message = {
            'type': 'message_deleted',
            'data': message_data
        }

        await websocket_manager.send_to_group(group_id, broadcast_message)

    @staticmethod
    async def broadcast_group_member_joined(group_id: int, member_data: dict):
        """广播新成员加入群聊"""
        broadcast_message = {
            'type': 'member_joined',
            'data': {
                'group_id': group_id,
                'member': member_data
            }
        }

        await websocket_manager.send_to_group(group_id, broadcast_message)

    @staticmethod
    async def broadcast_group_member_left(group_id: int, user_id: int):
        """广播成员离开群聊"""
        broadcast_message = {
            'type': 'member_left',
            'data': {
                'group_id': group_id,
                'user_id': user_id
            }
        }

        await websocket_manager.send_to_group(group_id, broadcast_message)

    @staticmethod
    async def broadcast_group_updated(group_data: dict):
        """广播群聊信息更新"""
        group_id = group_data.get('id')

        broadcast_message = {
            'type': 'group_updated',
            'data': group_data
        }

        await websocket_manager.send_to_group(group_id, broadcast_message)

    @staticmethod
    async def broadcast_user_status_changed(user_id: int, status: str):
        """广播用户状态变化"""
        broadcast_message = {
            'type': 'user_status_changed',
            'data': {
                'user_id': user_id,
                'status': status
            }
        }

        await websocket_manager.send_to_user(user_id, broadcast_message)

    @staticmethod
    async def update_group_last_message(group_id: int):
        """更新群聊最后消息时间"""
        try:
            from app.utils.database import get_db_connection

            conn = get_db_connection()
            cursor = conn.cursor()

            # 更新群聊表的更新时间
            cursor.execute("""
                UPDATE chat_groups
                SET updated_at = NOW()
                WHERE id = %s
            """, (group_id,))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"更新群聊最后消息时间失败: {e}")

# 全局广播服务实例
message_broadcast = MessageBroadcastService()