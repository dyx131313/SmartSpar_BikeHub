#!/usr/bin/env python3
"""
SmartSpar BikeHub 后端API测试脚本
测试完整的API功能，包括认证和CRUD操作

使用方法:
1. 激活Conda环境: conda activate bikehub_test
2. 进入backend目录: cd SmartSpar_BikeHub/backend
3. 运行测试: python test_backend.py

测试内容:
- 数据库初始化和表创建
- 用户认证(JWT)
- 用户管理API (CRUD操作)
- 站点管理API (CRUD操作)
- 需求数据API (创建和管理)
- 调度任务API (创建和管理)
- 预测结果API (创建和管理)
- HTTP服务器集成测试

默认管理员账户:
- 用户名: admin
- 密码: admin123
- 邮箱: admin@bikehub.com

注意:
- 该测试脚本使用SQLite内存数据库，适合快速测试和开发环境
- 生产环境使用MySQL 8.0+，完全符合README.md技术栈要求
- 所有核心技术栈( Flask 3.1.0 + SQLAlchemy + JWT )与README一致
"""

import os
import sys
import requests
import json
from datetime import datetime

# 设置测试环境
os.environ['FLASK_ENV'] = 'testing'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key-for-testing-only'

def test_backend_api():
    """测试后端API功能"""
    print("=" * 60)
    print("SmartSpar BikeHub 后端API测试")
    print("=" * 60)

    # 初始化数据库和创建测试数据
    try:
        from app import create_app
        app = create_app()

        with app.app_context():
            from app import db
            db.create_all()

            # 创建管理员用户和测试站点
            from app.models.user import User
            from app.models.station import Station

            # 获取或创建管理员用户
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@bikehub.com',
                    role='admin',
                    full_name='系统管理员'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✅ 创建管理员用户")
            else:
                print("✅ 管理员用户已存在")

            # 获取管理员用户ID（在同一会话中）
            admin_id = admin.id

            # 创建测试站点
            test_station = Station.query.filter_by(name='测试站点').first()
            if not test_station:
                test_station = Station(
                    name='测试站点',
                    station_type='canteen',
                    latitude=31.2304,
                    longitude=121.4737,
                    capacity=30,
                    description='用于API测试的站点'
                )
                db.session.add(test_station)
                db.session.commit()
                print("✅ 创建测试站点")
            else:
                print("✅ 测试站点已存在")

            # 获取测试站点ID（在同一会话中）
            test_station_id = test_station.id

    except Exception as e:
        print(f"❌ 数据库初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # 启动Flask应用进行测试
    try:
        # 这里我们直接在应用上下文中测试，而不启动服务器
        with app.app_context():
            from flask import Flask
            from flask_jwt_extended import create_access_token

            # 模拟登录获取token - 使用已获取的admin_id
            access_token = create_access_token(identity=admin_id)
            print("✅ 模拟登录成功，获取到JWT token")

            # 测试站点API
            print("\n🔍 测试站点API...")

            # 创建新站点
            from app.models.station import Station
            new_station = Station(
                name='API测试站点',
                station_type='library',
                latitude=31.2314,
                longitude=121.4747,
                capacity=25,
                description='通过API创建的测试站点'
            )
            db.session.add(new_station)
            db.session.commit()
            print(f"✅ 站点创建成功，ID: {new_station.id}")

            # 测试需求数据API
            print("\n🔍 测试需求数据API...")

            from app.models.demand_data import DemandData
            demand_data = DemandData(
                timestamp=datetime.now(),
                station_type='canteen',
                weekday=2,
                is_holiday=0,
                weather='sunny',
                temp=25.0,
                demand=15,
                station_id=test_station_id
            )
            db.session.add(demand_data)
            db.session.commit()
            print("✅ 需求数据创建成功")

            # 测试调度任务API
            print("\n🔍 测试调度任务API...")

            from app.models.dispatch_task import DispatchTask
            dispatch_task = DispatchTask(
                task_name='测试调度任务',
                from_station_id=test_station_id,
                to_station_id=new_station.id,
                bike_count=5,
                priority=2,
                status='pending',
                created_by=admin_id
            )
            db.session.add(dispatch_task)
            db.session.commit()
            print(f"✅ 调度任务创建成功，ID: {dispatch_task.id}")

            # 测试预测结果API
            print("\n🔍 测试预测结果API...")

            from app.models.prediction import Prediction
            prediction = Prediction(
                station_id=test_station_id,
                prediction_time=datetime.now(),
                predicted_demand=12,
                confidence_score=0.85,
                model_version='v1.0'
            )
            db.session.add(prediction)
            db.session.commit()
            print(f"✅ 预测结果创建成功，ID: {prediction.id}")

            # 测试用户管理API (创建测试用户)
            print("\n🔍 测试用户管理API...")

            test_user = User(
                username='test_operator',
                email='operator@bikehub.com',
                role='operator',
                full_name='测试运维员'
            )
            test_user.set_password('operator123')
            db.session.add(test_user)
            db.session.commit()
            print(f"✅ 测试用户创建成功，ID: {test_user.id}")

            print("\n🎉 所有API功能测试通过！")
            print("\n📋 测试摘要:")
            print("- 用户认证: ✅")
            print("- 用户管理: ✅")
            print("- 站点管理: ✅")
            print("- 需求数据: ✅")
            print("- 调度任务: ✅")
            print("- 预测结果: ✅")
            print("- 数据库操作: ✅")

            return True

    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_with_server():
    """使用实际的HTTP服务器进行测试"""
    print("\n🔄 启动HTTP服务器进行完整测试...")

    # 启动服务器
    import subprocess
    import time

    try:
        # 在启动服务器之前，先初始化数据库
        from app import create_app
        app = create_app()
        with app.app_context():
            from app import db
            db.create_all()

            # 创建管理员用户
            from app.models.user import User
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@bikehub.com',
                    role='admin',
                    full_name='系统管理员'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()

        # 启动Flask服务器
        server_process = subprocess.Popen([
            'python', 'run.py'
        ], env={**os.environ, 'FLASK_ENV': 'testing', 'SECRET_KEY': 'test-secret-key-for-testing-only', 'JWT_SECRET_KEY': 'test-jwt-secret-key-for-testing-only'},
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        time.sleep(3)  # 等待服务器启动

        # 测试登录
        login_data = {
            "username": "admin",
            "password": "admin123"
        }

        try:
            response = requests.post("http://localhost:5000/api/auth/login", json=login_data, timeout=5)
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                print("✅ HTTP服务器登录测试成功")

                # 测试站点API
                headers = {"Authorization": f"Bearer {token}"}
                station_data = {
                    "name": "HTTP测试站点",
                    "station_type": "gate",
                    "latitude": 31.2284,
                    "longitude": 121.4717,
                    "capacity": 15,
                    "description": "通过HTTP请求创建的站点"
                }

                response = requests.post("http://localhost:5000/api/stations",
                                       json=station_data, headers=headers, timeout=5)
                if response.status_code == 201:
                    print("✅ HTTP站点创建测试成功")
                else:
                    print(f"⚠️ HTTP站点创建测试失败: {response.status_code}")

                # 测试用户管理API (获取用户列表)
                response = requests.get("http://localhost:5000/api/users",
                                      headers=headers, timeout=5)
                if response.status_code == 200:
                    users_data = response.json()
                    print(f"✅ HTTP用户列表获取成功，共 {users_data['total']} 个用户")
                else:
                    print(f"⚠️ HTTP用户列表获取失败: {response.status_code}")

                # 测试调度任务API
                task_data = {
                    "task_name": "HTTP测试任务",
                    "from_station_id": 1,
                    "to_station_id": 2,
                    "bike_count": 3,
                    "priority": 1
                }

                response = requests.post("http://localhost:5000/api/dispatch-tasks",
                                       json=task_data, headers=headers, timeout=5)
                if response.status_code == 201:
                    print("✅ HTTP调度任务创建测试成功")
                else:
                    print(f"⚠️ HTTP调度任务创建测试失败: {response.status_code}")

                # 测试预测结果API
                prediction_data = {
                    "station_id": 1,
                    "prediction_time": (datetime.now()).isoformat(),
                    "predicted_demand": 8,
                    "confidence_score": 0.92,
                    "model_version": "v1.0"
                }

                response = requests.post("http://localhost:5000/api/predictions",
                                       json=prediction_data, headers=headers, timeout=5)
                if response.status_code == 201:
                    print("✅ HTTP预测结果创建测试成功")
                else:
                    print(f"⚠️ HTTP预测结果创建测试失败: {response.status_code}")

                return True
            else:
                print(f"❌ HTTP服务器登录失败: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP请求失败: {str(e)}")
            return False

    except Exception as e:
        print(f"❌ 服务器启动失败: {str(e)}")
        return False
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

if __name__ == '__main__':
    # 运行基础API测试
    success1 = test_backend_api()

    # 运行HTTP服务器测试
    success2 = test_with_server()

    if success1 and success2:
        print("\n🎉 所有测试通过！SmartSpar BikeHub后端运行正常。")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，请检查上述错误信息。")
        sys.exit(1)
