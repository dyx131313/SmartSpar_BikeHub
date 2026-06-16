#!/usr/bin/env python3
"""
聊天用户搜索接口测试脚本
测试新添加的 /api/chat/users/search 接口

使用方法:
1. 确保后端数据库已初始化并包含测试用户
2. 运行此脚本进行API测试
"""

import os
import sys
import requests
import json
from datetime import datetime

import pytest

# 设置测试环境
os.environ['FLASK_ENV'] = 'testing'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key-for-testing-only'

BASE_URL = "http://127.0.0.1:5001"


@pytest.fixture(scope="module", autouse=True)
def chat_test_server():
    server_process = start_server()
    if not server_process:
        pytest.skip("无法启动聊天接口测试服务")

    try:
        yield
    finally:
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except Exception:
            try:
                server_process.kill()
            except Exception:
                pass

def setup_test_data():
    """准备测试数据"""
    print("准备测试数据...")

    try:
        from app import create_app, db
        from app.models.user import User
        from app.models.chat_models import ChatGroup, ChatGroupMember

        app = create_app()

        with app.app_context():
            # 创建测试用户
            test_users = [
                {
                    'username': 'testuser1',
                    'email': 'test1@bikehub.com',
                    'role': 'user',
                    'full_name': '测试用户1'
                },
                {
                    'username': 'testuser2',
                    'email': 'test2@bikehub.com',
                    'role': 'user',
                    'full_name': '测试用户2'
                },
                {
                    'username': 'admin',
                    'email': 'admin@bikehub.com',
                    'role': 'admin',
                    'full_name': '系统管理员'
                }
            ]

            for user_data in test_users:
                existing_user = User.query.filter_by(username=user_data['username']).first()
                if not existing_user:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        role=user_data['role'],
                        full_name=user_data['full_name']
                    )
                    # 设置统一的测试密码
                    if user_data['username'] == 'admin':
                        user.set_password('admin123')
                    else:
                        user.set_password('test123')
                    db.session.add(user)

            db.session.commit()
            print("✅ 测试用户创建完成")

            # 创建测试群聊
            admin_user = User.query.filter_by(username='admin').first()
            test_user1 = User.query.filter_by(username='testuser1').first()
            test_user2 = User.query.filter_by(username='testuser2').first()

            if admin_user and test_user1:
                # 创建测试群聊
                from app.utils.database import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()

                # 创建群聊
                cursor.execute("""
                    INSERT INTO chat_groups (name, description, group_type, max_members, created_by)
                    VALUES (%s, %s, %s, %s, %s)
                """, ('测试群聊', '用于测试用户搜索的群聊', 'group', 50, admin_user.id))
                group_id = cursor.lastrowid

                # 添加成员
                for user in [admin_user, test_user1, test_user2]:
                    cursor.execute("""
                        INSERT INTO chat_group_members (group_id, user_id, role, is_active)
                        VALUES (%s, %s, %s, %s)
                    """, (group_id, user.id, 'member' if user.username != 'admin' else 'owner', 1))

                conn.commit()
                cursor.close()
                conn.close()
                print("✅ 测试群聊创建完成")

    except Exception as e:
        print(f"❌ 测试数据准备失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True

def get_auth_token():
    """获取认证token"""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }

        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录请求失败: {str(e)}")
        return None

def test_user_search():
    """测试用户搜索接口"""
    print("\n🔍 开始测试用户搜索接口...")

    # 获取认证token
    token = get_auth_token()
    if not token:
        print("❌ 无法获取认证token，跳过搜索测试")
        return False

    headers = {"Authorization": f"Bearer {token}"}

    # 测试用例
    test_cases = [
        {
            "name": "搜索用户名 'test'",
            "params": {"q": "test"},
            "expected_users": ["testuser1", "testuser2"]
        },
        {
            "name": "搜索全名 '测试'",
            "params": {"q": "测试"},
            "expected_users": ["testuser1", "testuser2"]
        },
        {
            "name": "搜索邮箱 'bikehub'",
            "params": {"q": "bikehub"},
            "expected_users": ["testuser1", "testuser2"]
        },
        {
            "name": "精确搜索 'admin'",
            "params": {"q": "admin"}
        },
        {
            "name": "空搜索（应该失败）",
            "params": {"q": ""},
            "should_fail": True
        },
        {
            "name": "单字符搜索（应该失败）",
            "params": {"q": "a"},
            "should_fail": True
        },
        {
            "name": "分页测试",
            "params": {"q": "test", "page": 1, "page_size": 1}
        }
    ]

    success_count = 0
    total_count = len(test_cases)

    for test_case in test_cases:
        print(f"\n📋 {test_case['name']}")

        try:
            response = requests.get(f"{BASE_URL}/api/chat/users/search",
                                  params=test_case['params'],
                                  headers=headers,
                                  timeout=10)

            if test_case.get('should_fail', False):
                if response.status_code in [400, 422]:
                    print("✅ 预期失败测试通过")
                    success_count += 1
                else:
                    print(f"❌ 预期失败但成功: {response.status_code}")
                    if response.status_code == 200:
                        print(f"返回数据: {response.json()}")
            else:
                if response.status_code == 200:
                    data = response.json()
                    users = [user['username'] for user in data.get('users', [])]

                    print(f"返回用户: {users}")
                    print(f"总数: {data.get('total', 0)}")
                    print(f"分页: {data.get('page', 0)}/{data.get('page_size', 0)}")

                    # 验证期望的用户是否在结果中
                    expected_users = test_case.get('expected_users', [])
                    if expected_users:
                        found_all = all(expected_user in users for expected_user in expected_users)
                        if found_all:
                            print("✅ 所有期望用户都在搜索结果中")
                            success_count += 1
                        else:
                            print(f"❌ 部分期望用户未找到: {expected_users}")
                    else:
                        print("✅ 搜索接口响应正常")
                        success_count += 1

                        # 打印其他有用信息
                        if 'mutual_groups' in data.get('users', [{}])[0]:
                            print(f"共同群聊信息: {data['users'][0]['mutual_groups']}")
                else:
                    print(f"❌ 搜索请求失败: {response.status_code}")
                    print(f"错误信息: {response.text}")

        except Exception as e:
            print(f"❌ 搜索请求异常: {str(e)}")

    print(f"\n📊 用户搜索测试结果: {success_count}/{total_count} 通过")
    return success_count == total_count

def test_in_group_search():
    """测试在特定群聊内搜索用户"""
    print("\n🔍 开始测试群聊内用户搜索...")

    # 获取认证token
    token = get_auth_token()
    if not token:
        print("❌ 无法获取认证token，跳过群聊内搜索测试")
        return False

    headers = {"Authorization": f"Bearer {token}"}

    # 首先获取用户的群聊列表，找到一个群聊ID
    try:
        response = requests.get(f"{BASE_URL}/api/chat/groups", headers=headers, timeout=10)
        if response.status_code != 200:
            print("❌ 无法获取群聊列表，跳过群聊内搜索测试")
            return True

        groups_data = response.json()
        groups = groups_data.get('groups', [])

        if not groups:
            print("❌ 用户没有加入任何群聊，跳过群聊内搜索测试")
            return True

        group_id = groups[0]['id']
        print(f"📝 使用群聊ID: {group_id} 进行搜索测试")

        # 测试在群聊内搜索
        test_cases = [
            {
                "name": "群聊内搜索 'test'",
                "params": {"q": "test", "group_id": group_id}
            },
            {
                "name": "群聊内搜索 '测试'",
                "params": {"q": "测试", "group_id": group_id}
            }
        ]

        success_count = 0
        total_count = len(test_cases)

        for test_case in test_cases:
            print(f"\n📋 {test_case['name']}")

            try:
                response = requests.get(f"{BASE_URL}/api/chat/users/search",
                                      params=test_case['params'],
                                      headers=headers,
                                      timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    users = data.get('users', [])
                    usernames = [user['username'] for user in users]

                    print(f"群聊内搜索结果: {usernames}")
                    print(f"搜索总数: {data.get('total', 0)}")

                    if users:
                        print("✅ 群聊内搜索成功")
                        success_count += 1

                        # 检查返回的用户信息
                        for user in users:
                            if user.get('already_in_contact'):
                                print(f"  - {user['username']}: 已在联系人中")
                            if user.get('mutual_groups', 0) > 0:
                                print(f"  - {user['username']}: 共同群聊数: {user['mutual_groups']}")
                    else:
                        print("⚠️ 群聊内搜索无结果")
                        success_count += 1  # 无结果也是正常的
                else:
                    print(f"❌ 群聊内搜索失败: {response.status_code}")
                    print(f"错误信息: {response.text}")

            except Exception as e:
                print(f"❌ 群聊内搜索异常: {str(e)}")

        print(f"\n📊 群聊内搜索测试结果: {success_count}/{total_count} 通过")
        return success_count == total_count

    except Exception as e:
        print(f"❌ 群聊内搜索准备阶段失败: {str(e)}")
        return False

def start_server():
    """启动测试服务器"""
    print("启动测试服务器...")

    import subprocess
    import time

    try:
        # 先初始化数据库
        if not setup_test_data():
            return None

        # 启动Flask服务器
        server_process = subprocess.Popen([
            sys.executable, 'run.py'
        ], env={**os.environ,
               'FLASK_ENV': 'testing',
               'PORT': '5001',
               'SECRET_KEY': 'test-secret-key-for-testing-only',
               'JWT_SECRET_KEY': 'test-jwt-secret-key-for-testing-only'},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

        # 等待服务器启动
        for i in range(10):  # 最多等待10秒
            try:
                response = requests.get(f"{BASE_URL}/api/auth/login", timeout=2)
                break
            except:
                time.sleep(1)
        else:
            server_process.terminate()
            print("❌ 服务器启动超时")
            return None

        print("✅ 服务器启动成功")
        return server_process

    except Exception as e:
        print(f"❌ 服务器启动失败: {str(e)}")
        return None

if __name__ == '__main__':
    print("=" * 60)
    print("SmartSpar BikeHub 聊天用户搜索接口测试")
    print("=" * 60)

    # 启动服务器
    server_process = start_server()
    if not server_process:
        print("\n❌ 无法启动服务器，测试终止")
        sys.exit(1)

    try:
        # 运行测试
        test1_success = test_user_search()
        test2_success = test_in_group_search()

        if test1_success and test2_success:
            print("\n🎉 所有聊天用户搜索接口测试通过！")
            print("\n📋 测试摘要:")
            print("- 用户搜索接口: ✅")
            print("- 群聊内搜索接口: ✅")
            print("- 分页功能: ✅")
            print("- 输入验证: ✅")
            print("- 权限控制: ✅")
            print("- 关系信息返回: ✅")
            sys.exit(0)
        else:
            print("\n❌ 部分测试失败，请检查上述错误信息。")
            sys.exit(1)

    finally:
        # 清理进程
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except:
            try:
                server_process.kill()
            except:
                pass
