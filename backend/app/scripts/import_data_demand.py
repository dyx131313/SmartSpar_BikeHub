#!/usr/bin/env python3
"""
简化的数据导入脚本
"""
import sys
import os
from dotenv import load_dotenv 


# 0. 先把 backend/.env 加载进来
backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(backend_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# 1. 如果未指定 FLASK_ENV，则默认使用开发环境（脚本不应强制覆盖已有环境）
if 'FLASK_ENV' not in os.environ:
    os.environ['FLASK_ENV'] = 'development'
if 'FLASK_CONFIG' not in os.environ:
    os.environ['FLASK_CONFIG'] = 'development'

# 2. 再把 backend/ 加入路径
sys.path.insert(0, backend_root)

from app import create_app, db
from app.utils.data_importer import DataImporter
import json

def simple_import():
    print("正在初始化应用...")
    app = create_app()
    with app.app_context():
        importer = DataImporter()

        data_dir = os.path.join(backend_root, 'data')
        stations_file = os.path.join(data_dir, 'api_stations.json')
        demands_file  = os.path.join(data_dir, 'api_demands.json')

        if os.path.exists(stations_file):
            print("导入站点数据...")
            result = importer.import_stations_from_json(stations_file)
            print(f"结果: {result['message']}")
        else:
            print(f"错误: 找不到 {stations_file}")
            return False

        if os.path.exists(demands_file):
            print("\n导入需求数据...")
            result = importer.import_demand_data_from_json(demands_file)
            print(f"结果: {result['message']}")
            if result.get('success'):
                print(f"\n摘要:\n  - 成功导入: {result.get('imported_count', 0)} 条\n  - 失败: {result.get('skipped_count', 0)} 条")
        else:
            print(f"错误: 找不到 {demands_file}")
            return False
        return True

if __name__ == "__main__":
    try:
        success = simple_import()
        print("\n✅ 数据导入完成！" if success else "\n❌ 数据导入失败！")
    except Exception as e:
        print(f"\n❌ 导入过程中发生错误: {e}")
        import traceback
        traceback.print_exc()