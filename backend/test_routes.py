#!/usr/bin/env python3
"""
测试路由注册情况
"""

import os
os.environ['FLASK_ENV'] = 'testing'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key-for-testing-only'

def test_routes():
    try:
        from app import create_app
        app = create_app()

        print("=== 检查路由注册情况 ===")

        # 查找聊天相关的路由
        chat_routes = []
        for rule in app.url_map.iter_rules():
            if 'chat' in rule.rule:
                chat_routes.append({
                    'rule': rule.rule,
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods)
                })

        print(f"找到 {len(chat_routes)} 个聊天相关路由:")
        for route in sorted(chat_routes, key=lambda x: x['rule']):
            print(f"  {route['rule']} -> {route['endpoint']} {route['methods']}")

        # 检查特定的路由
        target_routes = [
            '/api/chat/groups',
            '/api/chat/users/search',
            '/api/chat/search'
        ]

        print(f"\n=== 检查目标路由 ===")
        for target in target_routes:
            found = any(route['rule'] == target for route in chat_routes)
            status = "✓" if found else "✗"
            print(f"{status} {target}")

        if all(any(route['rule'] == target for route in chat_routes) for target in target_routes):
            print(f"\n所有目标路由都已正确注册！")
            return True
        else:
            print(f"\n部分路由缺失！")
            return False

    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_routes()
    exit(0 if success else 1)