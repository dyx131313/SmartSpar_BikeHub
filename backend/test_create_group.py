#!/usr/bin/env python3
"""
测试创建群聊功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置测试环境
os.environ['FLASK_ENV'] = 'testing'
os.environ['SECRET_KEY'] = 'xxxxyrXYR2352613'
os.environ['JWT_SECRET_KEY'] = 'xxxxyrXYR2352613'

BASE_URL = "http://localhost:5000/api"


from app.routes.chat import create_chat_group
from app.models.chat_models import ChatGroupCreate, GroupType



# 模拟请求数据
test_data = {
    "name": "测试群聊",
    "description": "这是一个测试群聊",
    "group_type": "public",
    "max_members": 50
}

# 创建ChatGroupCreate实例
try:
    group_data = ChatGroupCreate(**test_data)
    print(f"✓ ChatGroupCreate 验证成功")
    print(f"  - name: {group_data.name}")
    print(f"  - description: {group_data.description}")
    print(f"  - group_type: {group_data.group_type}")
    print(f"  - max_members: {group_data.max_members}")
    print(f"  - initial_members: {group_data.initial_members}")
    print(f"  - welcome_message: {group_data.welcome_message}")
except Exception as e:
    print(f"✗ ChatGroupCreate 验证失败: {str(e)}")
    sys.exit(1)

# 测试group_type.value
try:
    group_type_value = group_data.group_type.value
    print(f"✓ group_type.value 访问成功: {group_type_value}")
except AttributeError as e:
    print(f"✗ group_type.value 访问失败: {str(e)}")
    print("  尝试直接使用 group_type...")
    group_type_value = group_data.group_type if isinstance(group_data.group_type, str) else str(group_data.group_type)
    print(f"  使用 group_type: {group_type_value}")

print("\n测试完成！")