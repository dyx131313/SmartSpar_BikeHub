#!/usr/bin/env python3
"""
调度任务功能测试脚本
"""
import requests
import json
import time

# 基础URL
BASE_URL = "http://localhost:5000/api"

class DispatchTaskTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None

    def login(self, username, password):
        """登录获取token"""
        response = requests.post(f"{self.base_url}/auth/login", json={
            "username": username,
            "password": password
        })

        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            print(f"✅ 登录成功: {username}")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False

    def get_headers(self):
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def create_task(self, task_data):
        """创建调度任务"""
        response = requests.post(f"{self.base_url}/dispatch-tasks",
                               json=task_data, headers=self.get_headers())

        if response.status_code == 201:
            data = response.json()
            print(f"✅ 任务创建成功: {data['data']['task_name']}")
            return data['data']
        else:
            print(f"❌ 任务创建失败: {response.text}")
            return None

    def get_tasks(self):
        """获取任务列表"""
        response = requests.get(f"{self.base_url}/dispatch-tasks",
                              headers=self.get_headers())

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取到 {len(data['data'])} 个任务")
            return data['data']
        else:
            print(f"❌ 获取任务失败: {response.text}")
            return None

    def get_task(self, task_id):
        """获取单个任务"""
        response = requests.get(f"{self.base_url}/dispatch-tasks/{task_id}",
                              headers=self.get_headers())

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取任务成功: {data['data']['task_name']}")
            return data['data']
        else:
            print(f"❌ 获取任务失败: {response.text}")
            return None

    def update_task(self, task_id, update_data):
        """更新任务"""
        response = requests.put(f"{self.base_url}/dispatch-tasks/{task_id}",
                              json=update_data, headers=self.get_headers())

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 任务更新成功: {data['data']['task_name']}")
            return data['data']
        else:
            print(f"❌ 任务更新失败: {response.text}")
            return None

    def delete_task(self, task_id):
        """删除任务"""
        response = requests.delete(f"{self.base_url}/dispatch-tasks/{task_id}",
                                 headers=self.get_headers())

        if response.status_code == 200:
            print("✅ 任务删除成功")
            return True
        else:
            print(f"❌ 任务删除失败: {response.text}")
            return False

    def assign_task(self, task_id, operator_id):
        """分配任务"""
        response = requests.post(f"{self.base_url}/dispatch-tasks/{task_id}/assign",
                               json={"operator_id": operator_id},
                               headers=self.get_headers())

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 任务分配成功: {data['data']['task_name']}")
            return data['data']
        else:
            print(f"❌ 任务分配失败: {response.text}")
            return None

def test_dispatch_tasks():
    """测试调度任务的完整流程"""
    tester = DispatchTaskTester()

    print("=== 调度任务功能测试 ===\n")

    # 1. 登录调度员账户
    print("1. 登录调度员账户...")
    if not tester.login("dispatcher", "dispatcher123"):
        print("请先创建调度员用户: flask create-dispatcher")
        return

    # 2. 测试数据
    task_data = {
        "task_name": "教学楼到宿舍区单车调度",
        "from_station_id": 3,
        "to_station_id": 4,
        "bike_count": 15,
        "priority": 2,
        "assigned_to": 3
    }

    # 3. 创建任务
    print("\n2. 创建调度任务...")
    task = tester.create_task(task_data)
    if not task:
        return
    task_id = task['id']

    # 4. 获取任务列表
    print("\n3. 获取任务列表...")
    tasks = tester.get_tasks()

    # 5. 获取单个任务
    print("\n4. 获取单个任务...")
    tester.get_task(task_id)

    # 6. 更新任务
    print("\n5. 更新任务...")
    update_data = {
        "priority": 3,
        "bike_count": 20
    }
    tester.update_task(task_id, update_data)

    # 7. 分配任务给运维员
    print("\n6. 分配任务...")
    tester.assign_task(task_id, 3)

    # 8. 登录运维员账户查看任务
    print("\n7. 切换运维员账户查看任务...")
    operator_tester = DispatchTaskTester()
    if operator_tester.login("operator", "operator123"):
        operator_tester.get_task(task_id)

    # 9. 删除任务
    print("\n8. 删除任务...")
    tester.delete_task(task_id)

    print("\n=== 测试完成 ===")

def test_permissions():
    """测试权限控制"""
    print("\n=== 权限测试 ===")

    # 测试普通用户权限
    print("1. 测试普通用户权限...")
    user_tester = DispatchTaskTester()
    if user_tester.login("admin", "admin123"):  # 使用admin测试，因为可能没有普通用户
        # 尝试创建任务
        task_data = {
            "task_name": "测试任务",
            "from_station_id": 1,
            "to_station_id": 2,
            "bike_count": 5
        }
        user_tester.create_task(task_data)

    print("权限测试完成")

if __name__ == "__main__":
    print("开始测试调度任务功能...")
    print("请确保后端服务运行在 http://localhost:5000")
    print("请确保已创建测试用户: flask create-test-users")

    try:
        test_dispatch_tasks()
        test_permissions()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")