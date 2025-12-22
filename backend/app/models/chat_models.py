"""
群聊相关数据模型 (SQLAlchemy ORM)
"""
from datetime import datetime
from enum import Enum
from app import db
from sqlalchemy import func

class GroupType(str, Enum):
    """群聊类型枚举"""
    public = "public"
    private = "private"
    system = "system"

class MessageType(str, Enum):
    """消息类型枚举"""
    text = "text"
    image = "image"
    file = "file"
    system = "system"
    voice = "voice"

class MemberRole(str, Enum):
    """成员角色枚举"""
    owner = "owner"
    admin = "admin"
    member = "member"

class ChatGroup(db.Model):
    """群聊模型"""
    __tablename__ = 'chat_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    group_type = db.Column(db.Enum(GroupType), default=GroupType.public)
    max_members = db.Column(db.Integer, default=100)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系 (可选，视User模型定义而定，这里暂不定义backref以避免循环导入问题)
    # members = db.relationship('ChatGroupMember', backref='group', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'avatar_url': self.avatar_url,
            'group_type': self.group_type.value if hasattr(self.group_type, 'value') else self.group_type,
            'max_members': self.max_members,
            'created_by': self.created_by,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ChatGroupMember(db.Model):
    """群聊成员模型"""
    __tablename__ = 'chat_group_members'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('chat_groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.Enum(MemberRole), default=MemberRole.member)
    nickname = db.Column(db.String(50))
    is_muted = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.now)
    last_read_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'user_id': self.user_id,
            'role': self.role.value if hasattr(self.role, 'value') else self.role,
            'nickname': self.nickname,
            'is_muted': self.is_muted,
            'is_active': self.is_active,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_read_at': self.last_read_at.isoformat() if self.last_read_at else None
        }

class ChatMessage(db.Model):
    """群聊消息模型"""
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('chat_groups.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id')) # 私聊备用
    message_type = db.Column(db.Enum(MessageType), default=MessageType.text)
    content = db.Column(db.Text, nullable=False)
    file_url = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'))
    is_deleted = db.Column(db.Boolean, default=False)
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message_type': self.message_type.value if hasattr(self.message_type, 'value') else self.message_type,
            'content': self.content,
            'file_url': self.file_url,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'reply_to_id': self.reply_to_id,
            'is_deleted': self.is_deleted,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ChatMessageRead(db.Model):
    """消息阅读状态模型"""
    __tablename__ = 'chat_message_reads'

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read_at = db.Column(db.DateTime, default=datetime.now)
    
    # 联合唯一索引，确保用户对同一条消息只有一个阅读记录
    __table_args__ = (
        db.UniqueConstraint('message_id', 'user_id', name='uq_message_user_read'),
    )

class UserChatSetting(db.Model):
    """用户聊天设置"""
    __tablename__ = 'user_chat_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    setting_key = db.Column(db.String(50), nullable=False)
    setting_value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)