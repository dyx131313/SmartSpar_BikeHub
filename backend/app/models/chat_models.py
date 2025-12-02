"""
群聊相关数据模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class GroupType(str, Enum):
    """群聊类型枚举"""
    PUBLIC = "public"
    PRIVATE = "private"
    SYSTEM = "system"


class MessageType(str, Enum):
    """消息类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"
    VOICE = "voice"


class MemberRole(str, Enum):
    """成员角色枚举"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


# 群聊相关模型
class ChatGroupBase(BaseModel):
    """群聊基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="群聊名称")
    description: Optional[str] = Field(None, description="群聊描述")
    avatar_url: Optional[str] = Field(None, description="群聊头像URL")
    group_type: GroupType = Field(GroupType.PUBLIC, description="群聊类型")
    max_members: int = Field(100, ge=1, le=500, description="最大成员数量")


class ChatGroupCreate(ChatGroupBase):
    """创建群聊模型"""
    pass


class ChatGroupUpdate(BaseModel):
    """更新群聊模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="群聊名称")
    description: Optional[str] = Field(None, description="群聊描述")
    avatar_url: Optional[str] = Field(None, description="群聊头像URL")
    max_members: Optional[int] = Field(None, ge=1, le=500, description="最大成员数量")


class ChatGroup(ChatGroupBase):
    """群聊完整模型"""
    id: int
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    member_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ChatGroupWithMembers(ChatGroup):
    """包含成员信息的群聊模型"""
    members: List['ChatGroupMember'] = []


# 群聊成员相关模型
class ChatGroupMemberBase(BaseModel):
    """群聊成员基础模型"""
    group_id: int
    user_id: int
    role: MemberRole = Field(MemberRole.MEMBER, description="群内角色")
    nickname: Optional[str] = Field(None, max_length=50, description="群内昵称")
    is_muted: bool = Field(False, description="是否免打扰")


class ChatGroupMemberCreate(ChatGroupMemberBase):
    """添加群聊成员模型"""
    pass


class ChatGroupMemberUpdate(BaseModel):
    """更新群聊成员模型"""
    role: Optional[MemberRole] = Field(None, description="群内角色")
    nickname: Optional[str] = Field(None, max_length=50, description="群内昵称")
    is_muted: Optional[bool] = Field(None, description="是否免打扰")


class ChatGroupMember(ChatGroupMemberBase):
    """群聊成员完整模型"""
    id: int
    is_active: bool
    joined_at: datetime
    last_read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatGroupMemberWithUser(ChatGroupMember):
    """包含用户信息的群聊成员模型"""
    user: dict = {}  # 用户基本信息


# 消息相关模型
class ChatMessageBase(BaseModel):
    """消息基础模型"""
    group_id: Optional[int] = Field(None, description="群聊ID")
    receiver_id: Optional[int] = Field(None, description="接收者ID（私聊）")
    message_type: MessageType = Field(MessageType.TEXT, description="消息类型")
    content: str = Field(..., min_length=1, description="消息内容")
    reply_to_id: Optional[int] = Field(None, description="回复的消息ID")


class ChatMessageCreate(ChatMessageBase):
    """发送消息模型"""
    file_url: Optional[str] = Field(None, description="文件URL")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小（字节）")


class ChatMessageUpdate(BaseModel):
    """更新消息模型"""
    content: Optional[str] = Field(None, min_length=1, description="消息内容")


class ChatMessage(ChatMessageBase):
    """消息完整模型"""
    id: int
    sender_id: int
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    is_deleted: bool
    is_edited: bool
    edited_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageWithDetails(ChatMessage):
    """包含详细信息的消息模型"""
    sender: dict = {}  # 发送者基本信息
    reply_to: Optional['ChatMessage'] = None  # 回复的消息
    read_count: int = 0  # 已读人数
    is_read_by_me: bool = False  # 当前用户是否已读


# 消息阅读状态模型
class ChatMessageReadBase(BaseModel):
    """消息阅读状态基础模型"""
    message_id: int
    user_id: int


class ChatMessageRead(ChatMessageReadBase):
    """消息阅读状态完整模型"""
    id: int
    read_at: datetime

    class Config:
        from_attributes = True


# 用户聊天设置模型
class UserChatSettingBase(BaseModel):
    """用户聊天设置基础模型"""
    setting_key: str = Field(..., max_length=50, description="设置键")
    setting_value: str = Field(..., description="设置值")


class UserChatSettingCreate(UserChatSettingBase):
    """创建用户聊天设置模型"""
    pass


class UserChatSettingUpdate(BaseModel):
    """更新用户聊天设置模型"""
    setting_value: str = Field(..., description="设置值")


class UserChatSetting(UserChatSettingBase):
    """用户聊天设置完整模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# API响应模型
class ChatGroupListResponse(BaseModel):
    """群聊列表响应模型"""
    groups: List[ChatGroup]
    total: int
    page: int
    page_size: int


class ChatMessageListResponse(BaseModel):
    """消息列表响应模型"""
    messages: List[ChatMessageWithDetails]
    total: int
    page: int
    page_size: int
    has_more: bool


class ChatGroupMemberListResponse(BaseModel):
    """群聊成员列表响应模型"""
    members: List[ChatGroupMemberWithUser]
    total: int
    page: int
    page_size: int


class ChatStatisticsResponse(BaseModel):
    """聊天统计响应模型"""
    total_groups: int
    total_messages: int
    unread_messages: int
    active_groups: int


# WebSocket消息模型
class WebSocketMessage(BaseModel):
    """WebSocket消息模型"""
    type: str = Field(..., description="消息类型")
    data: dict = Field(..., description="消息数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class ChatNotificationMessage(WebSocketMessage):
    """聊天通知消息模型"""
    type: str = "chat_notification"
    data: dict = {
        "message_id": int,
        "group_id": Optional[int],
        "sender_id": int,
        "sender_name": str,
        "message_type": str,
        "content": str,
        "group_name": Optional[str],
        "is_private": bool
    }


# 文件上传模型
class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    url: str = Field(..., description="文件URL")
    filename: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小")
    content_type: str = Field(..., description="文件类型")


# 搜索模型
class ChatSearchRequest(BaseModel):
    """聊天搜索请求模型"""
    query: str = Field(..., min_length=1, max_length=100, description="搜索关键词")
    search_type: str = Field("all", description="搜索类型: groups, messages, users")
    group_id: Optional[int] = Field(None, description="限制搜索的群聊ID")


class ChatSearchResponse(BaseModel):
    """聊天搜索响应模型"""
    groups: List[ChatGroup] = []
    messages: List[ChatMessageWithDetails] = []
    users: List[dict] = []
    total_results: int