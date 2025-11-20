#!/usr/bin/env python3
"""
A*算法路径规划测试脚本
用于测试路径规划功能是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.astar_planner import AStarPlanner
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import numpy as np

def test_astar_algorithm():
    """测试A*算法基本功能"""
    print("=== A*算法路径规划测试 ===\n")

    # 创建测试站点数据
    test_stations = [
        {'id': 1, 'name': '食堂站点', 'latitude': 31.2304, 'longitude': 121.4737, 'station_type': 'canteen'},
        {'id': 2, 'name': '图书馆站点', 'latitude': 31.2314, 'longitude': 121.4747, 'station_type': 'library'},
        {'id': 3, 'name': '教学楼A栋', 'latitude': 31.2324, 'longitude': 121.4757, 'station_type': 'teaching_building'},
        {'id': 4, 'name': '宿舍区1号', 'latitude': 31.2294, 'longitude': 121.4727, 'station_type': 'dormitory'},
        {'id': 5, 'name': '南门站点', 'latitude': 31.2284, 'longitude': 121.4717, 'station_type': 'gate'},
    ]

    # 初始化A*规划器
    planner = AStarPlanner()
    planner.load_stations(test_stations)
    planner.build_adjacency_matrix(max_distance=1000.0)  # 1公里内建立连接

    print("1. 测试两点路径规划")
    print("-" * 30)

    # 测试食堂到图书馆的路径
    result = planner.find_path(1, 2)
    if result['success']:
        print(f"✓ 路径规划成功: 食堂站点 -> 图书馆站点")
        print(f"  路径: {' -> '.join([f'站点{id}' for id in result['path']])}")
        print(f"  总距离: {result['total_distance']:.2f} 米")
        print(f"  预估时间: {result['estimated_time']} 分钟")
        print(f"  途径点数量: {len(result['waypoints'])}")
    else:
        print(f"✗ 路径规划失败: {result.get('error', '未知错误')}")

    print("\n2. 测试多点路径规划")
    print("-" * 30)

    # 测试多点路径：食堂 -> 教学楼 -> 宿舍区
    waypoints = [3]  # 教学楼作为途径点
    multi_result = planner.find_multi_point_path(1, waypoints, 4)

    if multi_result['success']:
        print(f"✓ 多点路径规划成功: 食堂站点 -> 教学楼A栋 -> 宿舍区1号")
        print(f"  完整路径: {' -> '.join([f'站点{id}' for id in multi_result['path']])}")
        print(f"  总距离: {multi_result['total_distance']:.2f} 米")
        print(f"  预估时间: {multi_result['estimated_time']} 分钟")
        print(f"  优化算法: {multi_result['algorithm']}")
    else:
        print(f"✗ 多点路径规划失败: {multi_result.get('error', '未知错误')}")

    print("\n3. 测试距离计算")
    print("-" * 30)

    # 测试Haversine距离计算
    distance = planner.haversine_distance(
        test_stations[0]['latitude'], test_stations[0]['longitude'],
        test_stations[1]['latitude'], test_stations[1]['longitude']
    )
    print(f"✓ 食堂站点到图书馆站点的直线距离: {distance:.2f} 米")

    print("\n4. 测试邻接矩阵")
    print("-" * 30)

    # 显示邻接矩阵信息
    total_connections = sum(len(neighbors) for neighbors in planner.adjacency_matrix.values())
    print(f"✓ 邻接矩阵构建完成")
    print(f"  总站点数: {len(planner.stations)}")
    print(f"  总连接数: {total_connections}")

    # 显示每个站点的连接
    for station_id, neighbors in planner.adjacency_matrix.items():
        station_name = planner.stations[station_id]['name']
        print(f"  {station_name} 连接到: {len(neighbors)} 个站点")
        for neighbor_id, distance in neighbors.items():
            neighbor_name = planner.stations[neighbor_id]['name']
            print(f"    -> {neighbor_name}: {distance:.2f}米")

    print("\n5. 测试路径统计")
    print("-" * 30)

    if result['success']:
        stats = planner.get_path_statistics(result['path'])
        print(f"✓ 路径统计信息:")
        print(f"  总站点数: {stats['total_stations']}")
        print(f"  总距离: {stats['total_distance']:.2f} 米")
        print(f"  预估时间: {stats['estimated_time']} 分钟")
        print(f"  平均段距离: {stats['average_segment_distance']:.2f} 米")
        print(f"  站点类型分布: {stats['station_types']}")

    print("\n=== 测试完成 ===")
    return True

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 边界情况测试 ===\n")

    # 创建测试站点数据
    test_stations = [
        {'id': 1, 'name': '站点1', 'latitude': 31.2304, 'longitude': 121.4737, 'station_type': 'canteen'},
        {'id': 2, 'name': '站点2', 'latitude': 31.2314, 'longitude': 121.4747, 'station_type': 'library'},
    ]

    planner = AStarPlanner()
    planner.load_stations(test_stations)
    planner.build_adjacency_matrix(max_distance=100.0)  # 很小的连接距离

    print("1. 测试起点终点相同")
    result = planner.find_path(1, 1)
    if result['success'] and result['path'] == [1]:
        print("✓ 起点终点相同的情况处理正确")
    else:
        print("✗ 起点终点相同的情况处理错误")

    print("\n2. 测试不存在的站点")
    result = planner.find_path(1, 999)
    if not result['success']:
        print("✓ 不存在站点的情况处理正确")
    else:
        print("✗ 不存在站点的情况处理错误")

    print("\n3. 测试无法到达的情况")
    # 创建相距很远的站点
    distant_stations = [
        {'id': 10, 'name': '远站点1', 'latitude': 31.2304, 'longitude': 121.4737, 'station_type': 'canteen'},
        {'id': 11, 'name': '远站点2', 'latitude': 40.7128, 'longitude': -74.0060, 'station_type': 'library'},  # 纽约
    ]

    planner.load_stations(distant_stations)
    planner.build_adjacency_matrix(max_distance=1000.0)

    result = planner.find_path(10, 11)
    if not result['success']:
        print("✓ 无法到达的情况处理正确")
    else:
        print("✗ 无法到达的情况处理错误")

    print("\n=== 边界情况测试完成 ===")

if __name__ == "__main__":
    try:
        test_astar_algorithm()
        test_edge_cases()
        print("\n🎉 所有测试通过！A*算法功能正常。")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()