import numpy as np
import heapq
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from math import radians, cos, sin, asin, sqrt
import json

@dataclass
class Node:
    """路径规划节点"""
    station_id: int
    latitude: float
    longitude: float
    g_cost: float = float('inf')  # 从起点到当前节点的实际代价
    h_cost: float = 0.0  # 从当前节点到终点的启发式代价
    f_cost: float = float('inf')  # 总代价 f = g + h
    parent: Optional['Node'] = None

    def __lt__(self, other):
        return self.f_cost < other.f_cost

    def __eq__(self, other):
        return self.station_id == other.station_id

    def __hash__(self):
        return hash(self.station_id)

class AStarPlanner:
    """A*算法路径规划器"""

    def __init__(self):
        self.stations = {}
        self.adjacency_matrix = {}
        self.distance_cache = {}

    def load_stations(self, stations: List[Dict]):
        """加载站点数据"""
        for station in stations:
            self.stations[station['id']] = {
                'id': station['id'],
                'name': station['name'],
                'latitude': float(station['latitude']),
                'longitude': float(station['longitude']),
                'station_type': station['station_type']
            }

    def build_adjacency_matrix(self, max_distance: float = 2000.0):
        """构建邻接矩阵，max_distance为最大连接距离(米)"""
        station_ids = list(self.stations.keys())
        n = len(station_ids)

        for i, station1_id in enumerate(station_ids):
            station1 = self.stations[station1_id]
            self.adjacency_matrix[station1_id] = {}

            for j, station2_id in enumerate(station_ids):
                if i != j:
                    station2 = self.stations[station2_id]
                    distance = self.haversine_distance(
                        station1['latitude'], station1['longitude'],
                        station2['latitude'], station2['longitude']
                    )

                    if distance <= max_distance:
                        self.adjacency_matrix[station1_id][station2_id] = distance

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """计算两点间的Haversine距离(米)"""
        # 将十进制度数转化为弧度
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # haversine公式
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        # 地球半径(米)
        r = 6371000
        return c * r

    def heuristic_cost(self, node1: Dict, node2: Dict) -> float:
        """启发式函数：使用直线距离作为启发式代价"""
        return self.haversine_distance(
            node1['latitude'], node1['longitude'],
            node2['latitude'], node2['longitude']
        )

    def get_neighbors(self, station_id: int) -> List[Tuple[int, float]]:
        """获取节点的邻居和对应的距离"""
        if station_id not in self.adjacency_matrix:
            return []

        return [
            (neighbor_id, distance)
            for neighbor_id, distance in self.adjacency_matrix[station_id].items()
        ]

    def reconstruct_path(self, node: Node) -> List[int]:
        """重构路径"""
        path = []
        current = node
        while current is not None:
            path.append(current.station_id)
            current = current.parent
        return path[::-1]  # 反转路径

    def find_path(self, start_id: int, end_id: int) -> Dict:
        """使用A*算法寻找最优路径"""
        # 验证起点和终点
        if start_id not in self.stations or end_id not in self.stations:
            return {
                'success': False,
                'error': '起点或终点不存在',
                'path': [],
                'total_distance': 0,
                'estimated_time': 0
            }

        if start_id == end_id:
            return {
                'success': True,
                'path': [start_id],
                'total_distance': 0,
                'estimated_time': 0,
                'waypoints': []
            }

        # 初始化起点和终点节点
        start_station = self.stations[start_id]
        end_station = self.stations[end_id]

        start_node = Node(
            station_id=start_id,
            latitude=start_station['latitude'],
            longitude=start_station['longitude'],
            g_cost=0,
            h_cost=self.heuristic_cost(start_station, end_station),
            f_cost=self.heuristic_cost(start_station, end_station)
        )

        # 开放列表和关闭列表
        open_list = [start_node]
        closed_set: Set[int] = set()

        # 节点字典，用于快速查找和更新
        nodes = {start_id: start_node}

        while open_list:
            # 从开放列表中取出f代价最小的节点
            current_node = heapq.heappop(open_list)

            # 如果到达终点
            if current_node.station_id == end_id:
                path = self.reconstruct_path(current_node)
                waypoints = self.generate_waypoints(path)
                total_distance = current_node.g_cost
                estimated_time = self.estimate_travel_time(total_distance)

                return {
                    'success': True,
                    'path': path,
                    'waypoints': waypoints,
                    'total_distance': total_distance,
                    'estimated_time': estimated_time,
                    'algorithm': 'A*'
                }

            closed_set.add(current_node.station_id)

            # 检查所有邻居
            for neighbor_id, distance in self.get_neighbors(current_node.station_id):
                if neighbor_id in closed_set:
                    continue

                neighbor_station = self.stations[neighbor_id]
                tentative_g_cost = current_node.g_cost + distance

                # 如果邻居不在开放列表中，或者找到更好的路径
                if neighbor_id not in nodes or tentative_g_cost < nodes[neighbor_id].g_cost:
                    neighbor_node = Node(
                        station_id=neighbor_id,
                        latitude=neighbor_station['latitude'],
                        longitude=neighbor_station['longitude'],
                        g_cost=tentative_g_cost,
                        h_cost=self.heuristic_cost(neighbor_station, end_station),
                        f_cost=tentative_g_cost + self.heuristic_cost(neighbor_station, end_station),
                        parent=current_node
                    )

                    nodes[neighbor_id] = neighbor_node

                    if neighbor_id not in [node.station_id for node in open_list]:
                        heapq.heappush(open_list, neighbor_node)

        # 没有找到路径
        return {
            'success': False,
            'error': '无法找到有效路径',
            'path': [],
            'total_distance': 0,
            'estimated_time': 0
        }

    def find_multi_point_path(self, start_id: int, waypoints: List[int], end_id: int = None) -> Dict:
        """多点路径规划（TSP问题的近似解）"""
        if not waypoints:
            if end_id:
                return self.find_path(start_id, end_id)
            else:
                return {'success': False, 'error': '未指定终点'}

        # 如果没有指定终点，使用最后一个途径点作为终点
        if end_id is None:
            end_id = waypoints[-1]

        # 简单的贪心算法：每次选择距离当前位置最近的未访问点
        full_path = [start_id]
        remaining_points = waypoints.copy() if end_id not in waypoints else waypoints[:-1]
        current_id = start_id
        total_distance = 0
        all_waypoints = []

        while remaining_points:
            # 找到距离当前位置最近的点
            nearest_point = None
            nearest_distance = float('inf')
            nearest_path_result = None

            for point in remaining_points:
                path_result = self.find_path(current_id, point)
                if path_result['success'] and path_result['total_distance'] < nearest_distance:
                    nearest_point = point
                    nearest_distance = path_result['total_distance']
                    nearest_path_result = path_result

            if nearest_point is None:
                return {
                    'success': False,
                    'error': f'无法从位置 {current_id} 到达任何剩余点',
                    'path': full_path
                }

            # 添加到路径中
            if len(nearest_path_result['path']) > 1:
                full_path.extend(nearest_path_result['path'][1:])
                all_waypoints.extend(nearest_path_result['waypoints'])

            total_distance += nearest_distance
            current_id = nearest_point
            remaining_points.remove(nearest_point)

        # 最后前往终点
        if end_id != current_id:
            final_path_result = self.find_path(current_id, end_id)
            if final_path_result['success']:
                if len(final_path_result['path']) > 1:
                    full_path.extend(final_path_result['path'][1:])
                    all_waypoints.extend(final_path_result['waypoints'])
                total_distance += final_path_result['total_distance']
            else:
                return {
                    'success': False,
                    'error': f'无法从最后一个途径点到达终点 {end_id}',
                    'path': full_path
                }

        estimated_time = self.estimate_travel_time(total_distance)

        return {
            'success': True,
            'path': full_path,
            'waypoints': all_waypoints,
            'total_distance': total_distance,
            'estimated_time': estimated_time,
            'algorithm': 'A* Multi-Point (Greedy)',
            'optimized_points': len(waypoints)
        }

    def generate_waypoints(self, path: List[int]) -> List[Dict]:
        """生成路径的详细坐标点"""
        waypoints = []
        for i, station_id in enumerate(path):
            station = self.stations[station_id]
            waypoints.append({
                'order': i + 1,
                'station_id': station_id,
                'station_name': station['name'],
                'latitude': station['latitude'],
                'longitude': station['longitude'],
                'station_type': station['station_type']
            })
        return waypoints

    def estimate_travel_time(self, distance: float, speed: float = 15.0) -> int:
        """估算行驶时间（分钟），默认速度15km/h（电动车）"""
        if distance == 0:
            return 0
        # 距离(米) / 速度(米/分钟) = 时间(分钟)
        speed_m_per_min = speed * 1000 / 60
        time_minutes = distance / speed_m_per_min
        return int(round(time_minutes))

    def find_alternative_paths(self, start_id: int, end_id: int, max_paths: int = 3) -> List[Dict]:
        """寻找多条备选路径"""
        # 这里可以实现A*的变种来寻找多条路径
        # 简化实现：返回相同的路径多次，实际应用中可以使用不同的启发式函数
        paths = []
        main_path = self.find_path(start_id, end_id)

        if main_path['success']:
            paths.append(main_path)

            # 可以在这里添加寻找其他路径的逻辑
            # 例如：使用不同的代价函数，或者临时禁用某些边

        return paths

    def get_path_statistics(self, path: List[int]) -> Dict:
        """获取路径统计信息"""
        if len(path) < 2:
            return {
                'total_stations': len(path),
                'total_distance': 0,
                'estimated_time': 0,
                'station_types': {}
            }

        total_distance = 0
        station_types = {}

        # 计算总距离和站点类型统计
        for i in range(len(path) - 1):
            station1 = self.stations[path[i]]
            station2 = self.stations[path[i + 1]]
            distance = self.haversine_distance(
                station1['latitude'], station1['longitude'],
                station2['latitude'], station2['longitude']
            )
            total_distance += distance

            # 统计站点类型
            station_type = station1['station_type']
            station_types[station_type] = station_types.get(station_type, 0) + 1

        # 最后一个站点
        last_station = self.stations[path[-1]]
        station_type = last_station['station_type']
        station_types[station_type] = station_types.get(station_type, 0) + 1

        estimated_time = self.estimate_travel_time(total_distance)

        return {
            'total_stations': len(path),
            'total_distance': total_distance,
            'estimated_time': estimated_time,
            'station_types': station_types,
            'average_segment_distance': total_distance / (len(path) - 1) if len(path) > 1 else 0
        }