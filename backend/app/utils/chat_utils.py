"""
群聊工具函数
"""
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def validate_file_type(filename: str) -> str:
    """
    验证文件类型
    """
    allowed_types = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar']

    # 获取文件扩展名
    if '.' in filename:
        ext = filename.lower().split('.')[-1]
        if ext in allowed_types:
            return ext

    return 'unknown'

def format_message_content(content: str, message_type: str) -> Dict[str, Any]:
    """
    格式化消息内容
    """
    try:
        if message_type == 'system':
            return {
                'content': content,
                'is_system': True,
                'formatted': content
            }

        elif message_type == 'text':
            # 简单的文本消息
            return {
                'content': content,
                'is_system': False,
                'formatted': content
            }

        elif message_type == 'image':
            return {
                'content': content,
                'is_system': False,
                'formatted': f'<img src="{content}" alt="图片消息" />',
                'is_image': True
            }

        elif message_type == 'file':
            return {
                'content': content,
                'is_system': False,
                'formatted': f'<div class="file-message">📎 {content}</div>',
                'is_file': True
            }

        else:
            return {
                'content': content,
                'is_system': False,
                'formatted': content
            }

    except Exception as e:
        logger.error(f"格式化消息内容失败: {str(e)}")
        return {
            'content': content,
                'is_system': False,
                'formatted': content,
            'error': str(e)
        }

def parse_message_content(message_data: Dict[str, Any]) -> str:
    """
    解析消息数据
    """
    try:
        if isinstance(message_data, str):
            return message_data
        elif isinstance(message_data, dict):
            return message_data.get('content', '')
        else:
            return str(message_data)

    except Exception as e:
        logger.error(f"解析消息数据失败: {str(e)}")
        return ''

def get_file_size_display(size_bytes: int) -> str:
    """
    获取文件大小的显示格式
    """
    if size_bytes == 0:
        return '0 B'

    size_kb = size_bytes / 1024
    if size_kb < 1:
        return f"{size_bytes} B"
    elif size_kb < 1024:
        return f"{size_kb:.1f} KB"
    else:
        size_mb = size_kb / 1024
        if size_mb < 1024:
            return f"{size_mb:.1f} MB"
        else:
            return f"{size_mb/1024:.1f} GB"

def validate_group_name(name: str) -> tuple[bool, str]:
    """
    验证群聊名称
    """
    if not name or not name.strip():
        return False, "群聊名称不能为空"

    if len(name.strip()) < 2:
        return False, "群聊名称至少需要2个字符"

    if len(name.strip()) > 100:
        return False, "群聊名称不能超过100个字符"

    # 检查是否包含特殊字符
    invalid_chars = ['<', '>', '"', "'", '\\', '&']
    for char in invalid_chars:
        if char in name:
            return False, f"群聊名称不能包含字符: {char}"

    return True, "群聊名称验证通过"

def validate_message_content(content: str) -> tuple[bool, str]:
    """
    验证消息内容
    """
    if not content or not content.strip():
        return False, "消息内容不能为空"

    if len(content.strip()) > 1000:
        return False, "消息内容不能超过1000个字符"

    return True, "消息内容验证通过"

def safe_json_loads(json_str: str) -> Dict[str, Any]:
    """
    安全的JSON加载
    """
    try:
        if not json_str or not json_str.strip():
            return {}
        return json.loads(json_str)
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"JSON解析失败: {str(e)}")
        return {}

def safe_json_dumps(obj: Any) -> str:
    """
    安全的JSON序列化
    """
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError) as e:
        logger.error(f"JSON序列化失败: {str(e)}")
        return json.dumps({})

def get_timestamp() -> str:
    """
    获取当前时间戳字符串
    """
    return datetime.now().isoformat()

def parse_pagination_params(page: int = 1, page_size: int = 20, max_page_size: int = 100) -> Dict[str, int]:
    """
    解析分页参数
    """
    page = max(1, min(page, 100))
    page_size = max(1, min(page_size, max_page_size))
    offset = (page - 1) * page_size

    return {
        'page': page,
        'page_size': page_size,
        'offset': offset,
        'limit': page_size
    }

def check_group_permission(user_role: str, required_role: str) -> bool:
    """
    检查群聊权限
    """
    role_hierarchy = {
        'owner': 0,
        'admin': 1,
        'member': 2
    }

    try:
        user_level = role_hierarchy.get(user_role, 3)  # 默认为member
        required_level = role_hierarchy.get(required_role, 3)
        return user_level <= required_level
    except Exception:
        return False

def create_error_response(message: str, status_code: int = 500, data: Any = None) -> Dict[str, Any]:
    """
    创建统一的错误响应
    """
    return {
        'error': message,
        'message': message,
        'status_code': status_code,
        'data': data,
        'timestamp': get_timestamp()
    }

def create_success_response(message: str, data: Any = None, status_code: int = 200) -> Dict[str, Any]:
    """
    创建统一的成功响应
    """
    return {
        'message': message,
        'status_code': status_code,
        'data': data,
        'timestamp': get_timestamp()
    }