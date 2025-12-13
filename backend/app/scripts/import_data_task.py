#!/usr/bin/env python3
"""
简化的调度任务导入脚本
"""
import sys
import os
from dotenv import load_dotenv 

# 0. 先把 backend/.env 加载进来
backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(backend_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# 1. 强制开发环境，避开 ProductionConfig 检查
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_CONFIG'] = 'development'

# 2. 再把 backend/ 加入路径
sys.path.insert(0, backend_root)

from app import create_app, db
from app.utils.data_importer import DataImporter
import json
import pandas as pd

def simple_import_tasks():
    print("正在初始化应用...")
    app = create_app()
    with app.app_context():
        importer = DataImporter()

        data_dir = os.path.join(backend_root, 'data')
        tasks_csv_file = os.path.join(data_dir, 'api_dispatch_tasks.csv')
        tasks_json_file = os.path.join(data_dir, 'api_dispatch_tasks.json')

        # 先尝试 JSON 文件
        if os.path.exists(tasks_json_file):
            print("导入调度任务数据（JSON）...")
            result = importer.import_dispatch_tasks(tasks_json_file)
            print(f"结果: {result['message']}")
            if result.get('success'):
                print(f"\n摘要:\n  - 成功导入: {result.get('imported_count', 0)} 条\n  - 失败/跳过: {result.get('skipped_count', 0)} 条")
            return result.get('success', False)
        
        # 再尝试 CSV 文件
        elif os.path.exists(tasks_csv_file):
            print("导入调度任务数据（CSV）...")
            
            # 读取 CSV 并转换为 JSON 格式
            df = pd.read_csv(tasks_csv_file)
            tasks_data = df.to_dict('records')
            
            # 导入数据
            result = importer.import_dispatch_tasks(tasks_data)
            print(f"结果: {result['message']}")
            if result.get('success'):
                print(f"\n摘要:\n  - 成功导入: {result.get('imported_count', 0)} 条\n  - 失败/跳过: {result.get('skipped_count', 0)} 条")
            return result.get('success', False)
        
        else:
            print(f"错误: 找不到调度任务数据文件")
            print(f"请确保以下文件之一存在:")
            print(f"  - {tasks_csv_file}")
            print(f"  - {tasks_json_file}")
            return False

if __name__ == "__main__":
    try:
        success = simple_import_tasks()
        print("\n✅ 调度任务数据导入完成！" if success else "\n❌ 调度任务数据导入失败！")
    except Exception as e:
        print(f"\n❌ 导入过程中发生错误: {e}")
        import traceback
        traceback.print_exc()