#!/usr/bin/env python3
"""
A*算法模块验证脚本
确保所有功能正常工作
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'code', 'SmartSpar_BikeHub', 'backend'))

def test_astar_module():
    """测试A*算法模块是否正常工作"""
    print("🔍 A*算法模块验证")
    print("-" * 30)

    try:
        from app.utils.astar_planner import AStarPlanner
        print("✅ A*算法模块导入成功")

        # 创建规划器
        planner = AStarPlanner()
        print("✅ A*规划器实例化成功")

        # 测试数据加载
        test_stations = [
            {'id': 1, 'name': '测试站点1', 'latitude': 31.2304, 'longitude': 121.4737, 'station_type': 'canteen'},
            {'id': 2, 'name': '测试站点2', 'latitude': 31.2314, 'longitude': 121.4747, 'station_type': 'library'},
        ]
        planner.load_stations(test_stations)
        print("✅ 站点数据加载成功")

        # 测试邻接矩阵构建
        planner.build_adjacency_matrix(max_distance=1000.0)
        print("✅ 邻接矩阵构建成功")

        # 测试路径规划
        result = planner.find_path(1, 2)
        if result['success']:
            print("✅ 路径规划功能正常")
        else:
            print("❌ 路径规划功能异常")

        # 测试多点路径规划
        multi_result = planner.find_multi_point_path(1, [2], 1)
        if multi_result['success']:
            print("✅ 多点路径规划功能正常")
        else:
            print("❌ 多点路径规划功能异常")

        print("\n🎉 所有A*算法功能验证通过!")
        return True

    except Exception as e:
        print(f"❌ A*算法模块验证失败: {e}")
        return False

def test_dependencies():
    """测试依赖包"""
    print("🔍 依赖包验证")
    print("-" * 30)

    required_packages = ['numpy', 'json', 'datetime', 'heapq']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 需要安装")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n缺少依赖包: {missing_packages}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False
    else:
        print("\n✅ 所有依赖包已安装")
        return True

if __name__ == "__main__":
    print("=" * 50)
    print("   A*算法路径规划模块 - 系统验证")
    print("=" * 50)

    deps_ok = test_dependencies()
    module_ok = test_astar_module()

    if deps_ok and module_ok:
        print("\n🚀 系统验证完成，可以运行演示脚本!")
        print("运行命令: python astar_demo.py")
    else:
        print("\n⚠️  请解决上述问题后再运行演示脚本")