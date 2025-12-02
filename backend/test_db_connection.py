#!/usr/bin/env python3
"""
测试数据库连接脚本
"""
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_mysql_connection():
    """测试MySQL连接"""
    try:
        import pymysql

        print("=== 数据库连接测试 ===")
        print(f"MYSQL_HOST: {os.getenv('MYSQL_HOST', 'localhost')}")
        print(f"MYSQL_USER: {os.getenv('MYSQL_USER', 'root')}")
        print(f"MYSQL_DATABASE: {os.getenv('MYSQL_DATABASE', 'bikehub')}")
        print(f"MYSQL_PORT: {os.getenv('MYSQL_PORT', '3306')}")

        # 测试连接
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'bikehub'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        print("✅ 数据库连接成功！")

        # 测试查询
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"查询测试结果: {result}")

        # 测试群聊表是否存在
        cursor.execute("SHOW TABLES LIKE 'chat_%'")
        tables = cursor.fetchall()
        print(f"群聊相关表: {[table[0] for table in tables]}")

        connection.close()
        return True

    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

def test_api_imports():
    """测试API模块导入"""
    try:
        from app.routes.chat import chat_bp
        print("✅ chat蓝图导入成功")
        return True
    except Exception as e:
        print(f"❌ chat蓝图导入失败: {str(e)}")
        return False

if __name__ == '__main__':
    print("开始后端服务诊断...")

    # 测试数据库连接
    db_ok = test_mysql_connection()

    # 测试API导入
    api_ok = test_api_imports()

    if db_ok and api_ok:
        print("✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 存在问题，请检查配置")
        sys.exit(1)