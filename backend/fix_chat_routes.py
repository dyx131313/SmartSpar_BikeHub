#!/usr/bin/env python3
"""
修复chat.py中所有的路由装饰器
"""

import re

def fix_chat_routes():
    file_path = "E:/软件工程/project/SmartSpar_BikeHub/backend/app/routes/chat.py"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换所有的@chat_bp.route()为@api_bp.route()
    patterns_to_fix = [
        (r'@chat_bp\.route\(\'/groups/<int:group_id>/members\'', "@api_bp.route(\"/chat/groups/<int:group_id>/members\")"),
        (r'@chat_bp\.route\(\'/groups/<int:group_id>/members\', methods=\[\'POST\']\)', "@api_bp.route(\"/chat/groups/<int:group_id>/members\", methods=['POST'])"),
        (r'@chat_bp\.route\(\'/groups/<int:group_id>/messages\', methods=\[\'GET\']\)', "@api_bp.route(\"/chat/groups/<int:group_id>/messages\", methods=['GET'])"),
        (r'@chat_bp\.route\(\'/groups/<int:group_id>/messages\', methods=\[\'POST\']\)', "@api_bp.route(\"/chat/groups/<int:group_id>/messages\", methods=['POST'])"),
        (r'@chat_bp\.route\(\'/messages/<int:message_id>/read\', methods=\[\'POST\']\)', "@api_bp.route(\"/chat/messages/<int:message_id>/read\", methods=['POST'])"),
        (r'@chat_bp\.route\(\'/search\', methods=\[\'GET\']\)', "@api_bp.route(\"/chat/search\", methods=['GET'])"),
        (r'@chat_bp\.route\(\'/statistics\', methods=\[\'GET\']\)', "@api_bp.route(\"/chat/statistics\", methods=['GET'])"),
        (r'@chat_bp\.route\(\'/admin/groups\', methods=\[\'GET\']\)', "@api_bp.route(\"/chat/admin/groups\", methods=['GET'])"),
    ]

    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content)

    # 通用替换其他可能遗漏的路由
    content = re.sub(r'@chat_bp\.route\(([^)]+)\)', lambda m: f"@api_bp.route({m.group(1).replace('/chat', '/chat')})", content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("路由装饰器修复完成")

if __name__ == '__main__':
    fix_chat_routes()