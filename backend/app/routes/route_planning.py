from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.station import Station
from app.models.route_plan import RoutePlan, RouteHistory
from app.models.user import User
from app.models.dispatch_task import DispatchTask
from app.utils.astar_planner import AStarPlanner
from app.routes import api_bp

# 全局A*规划器实例
_astar_planner = None

def get_astar_planner():
    """获取A*规划器实例，确保数据已加载"""
    global _astar_planner
    if _astar_planner is None:
        _astar_planner = AStarPlanner()
        # 加载所有站点数据
        stations = Station.query.all()
        stations_data = [station.to_dict() for station in stations]
        _astar_planner.load_stations(stations_data)
        _astar_planner.build_adjacency_matrix()
    return _astar_planner

@api_bp.route('/route-planning/plan', methods=['POST'])
@jwt_required()
def create_route_plan():
    """生成路径规划"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()

        # 验证必填字段
        required_fields = ['plan_name', 'start_station_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        # 验证站点是否存在
        start_station = Station.query.get(data['start_station_id'])
        if not start_station:
            return jsonify({'error': '起点站点不存在'}), 400

        # 确定终点站点
        end_station_id = data.get('end_station_id')
        if not end_station_id and data.get('waypoints'):
            # 如果没有指定终点，使用最后一个途径点
            end_station_id = data['waypoints'][-1]

        if not end_station_id:
            return jsonify({'error': '必须指定终点站点或途径点'}), 400

        end_station = Station.query.get(end_station_id)
        if not end_station:
            return jsonify({'error': '终点站点不存在'}), 400

        # 获取A*规划器并计算路径
        planner = get_astar_planner()

        # 验证途径点是否存在
        waypoints = data.get('waypoints', [])
        for waypoint_id in waypoints:
            if not Station.query.get(waypoint_id):
                return jsonify({'error': f'途径点 {waypoint_id} 不存在'}), 400

        # 计算路径
        if waypoints:
            # 多点路径规划
            route_result = planner.find_multi_point_path(
                start_station_id=data['start_station_id'],
                waypoints=waypoints,
                end_id=end_station_id
            )
        else:
            # 两点路径规划
            route_result = planner.find_path(
                start_id=data['start_station_id'],
                end_id=end_station_id
            )

        if not route_result['success']:
            return jsonify({
                'error': '路径规划失败',
                'details': route_result.get('error', '未知错误')
            }), 400

        # 验证关联的调度任务
        task_id = data.get('task_id')
        if task_id:
            task = DispatchTask.query.get(task_id)
            if not task:
                return jsonify({'error': '关联的调度任务不存在'}), 400

        # 创建路径规划记录
        route_plan = RoutePlan(
            plan_name=data['plan_name'],
            start_station_id=data['start_station_id'],
            end_station_id=end_station_id,
            path_data=route_result,
            total_distance=route_result['total_distance'],
            estimated_time=route_result['estimated_time'],
            algorithm_used=route_result['algorithm'],
            waypoints=waypoints if waypoints else None,
            is_multi_point=bool(waypoints),
            task_id=task_id,
            bike_capacity=data.get('bike_capacity', 20),
            optimization_goal=data.get('optimization_goal', 'shortest'),
            priority=data.get('priority', 1),
            created_by=current_user_id
        )

        db.session.add(route_plan)
        db.session.commit()

        return jsonify({
            'message': '路径规划创建成功',
            'data': route_plan.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/route-planning', methods=['GET'])
@jwt_required()
def get_route_plans():
    """获取路径规划列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        start_station_id = request.args.get('start_station_id', type=int)
        end_station_id = request.args.get('end_station_id', type=int)

        query = RoutePlan.query

        if status:
            query = query.filter(RoutePlan.status == status)
        if start_station_id:
            query = query.filter(RoutePlan.start_station_id == start_station_id)
        if end_station_id:
            query = query.filter(RoutePlan.end_station_id == end_station_id)

        pagination = query.order_by(RoutePlan.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'data': [plan.to_dict() for plan in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/route-planning/<int:id>', methods=['GET'])
@jwt_required()
def get_route_plan(id):
    """获取单个路径规划"""
    try:
        route_plan = RoutePlan.query.get_or_404(id)
        return jsonify({'data': route_plan.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/route-planning/<int:id>', methods=['PUT'])
@jwt_required()
def update_route_plan(id):
    """更新路径规划"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        route_plan = RoutePlan.query.get_or_404(id)
        data = request.get_json()

        # 权限检查：只有创建者和管理员可以修改
        if route_plan.created_by != current_user_id and current_user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403

        # 更新字段
        if 'plan_name' in data:
            route_plan.plan_name = data['plan_name']
        if 'bike_capacity' in data:
            route_plan.bike_capacity = data['bike_capacity']
        if 'optimization_goal' in data:
            route_plan.optimization_goal = data['optimization_goal']
        if 'priority' in data:
            route_plan.priority = data['priority']
        if 'status' in data:
            route_plan.status = data['status']

        db.session.commit()

        return jsonify({
            'message': '路径规划更新成功',
            'data': route_plan.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/route-planning/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_route_plan(id):
    """删除路径规划"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        route_plan = RoutePlan.query.get_or_404(id)

        # 权限检查：只有创建者和管理员可以删除
        if route_plan.created_by != current_user_id and current_user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403

        db.session.delete(route_plan)
        db.session.commit()

        return jsonify({'message': '路径规划删除成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/route-planning/calculate', methods=['POST'])
@jwt_required()
def calculate_route():
    """仅计算路径，不保存到数据库"""
    try:
        data = request.get_json()

        # 验证必填字段
        if 'start_station_id' not in data:
            return jsonify({'error': '缺少起点站点ID'}), 400

        # 验证站点是否存在
        start_station = Station.query.get(data['start_station_id'])
        if not start_station:
            return jsonify({'error': '起点站点不存在'}), 400

        end_station_id = data.get('end_station_id')
        if not end_station_id and data.get('waypoints'):
            end_station_id = data['waypoints'][-1]

        if not end_station_id:
            return jsonify({'error': '必须指定终点站点或途径点'}), 400

        end_station = Station.query.get(end_station_id)
        if not end_station:
            return jsonify({'error': '终点站点不存在'}), 400

        # 获取A*规划器并计算路径
        planner = get_astar_planner()

        # 验证途径点是否存在
        waypoints = data.get('waypoints', [])
        for waypoint_id in waypoints:
            if not Station.query.get(waypoint_id):
                return jsonify({'error': f'途径点 {waypoint_id} 不存在'}), 400

        # 计算路径
        if waypoints:
            # 多点路径规划
            route_result = planner.find_multi_point_path(
                start_station_id=data['start_station_id'],
                waypoints=waypoints,
                end_id=end_station_id
            )
        else:
            # 两点路径规划
            route_result = planner.find_path(
                start_id=data['start_station_id'],
                end_id=end_station_id
            )

        if not route_result['success']:
            return jsonify({
                'error': '路径计算失败',
                'details': route_result.get('error', '未知错误')
            }), 400

        # 添加站点详细信息
        route_result['start_station'] = start_station.to_dict()
        route_result['end_station'] = end_station.to_dict()

        if waypoints:
            waypoint_stations = []
            for waypoint_id in waypoints:
                station = Station.query.get(waypoint_id)
                waypoint_stations.append(station.to_dict())
            route_result['waypoint_stations'] = waypoint_stations

        return jsonify({
            'message': '路径计算成功',
            'data': route_result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/route-planning/multi-point', methods=['POST'])
@jwt_required()
def calculate_multi_point_route():
    """多点路径规划"""
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['start_station', 'waypoints']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        # 验证起点和终点
        start_station_id = data['start_station']
        waypoints = data['waypoints']
        end_station_id = data.get('end_station', waypoints[-1])

        # 获取站点
        start_station = Station.query.get(start_station_id)
        if not start_station:
            return jsonify({'error': '起点站点不存在'}), 400

        end_station = Station.query.get(end_station_id)
        if not end_station:
            return jsonify({'error': '终点站点不存在'}), 400

        # 验证途径点
        for waypoint_id in waypoints:
            if not Station.query.get(waypoint_id):
                return jsonify({'error': f'途径点 {waypoint_id} 不存在'}), 400

        # 获取A*规划器
        planner = get_astar_planner()

        # 计算多点路径
        route_result = planner.find_multi_point_path(
            start_id=start_station_id,
            waypoints=waypoints,
            end_id=end_station_id
        )

        if not route_result['success']:
            return jsonify({
                'error': '多点路径规划失败',
                'details': route_result.get('error', '未知错误')
            }), 400

        # 获取备选路径
        alternative_paths = planner.find_alternative_paths(
            start_station_id, end_station_id, max_paths=3
        )

        return jsonify({
            'message': '多点路径规划成功',
            'data': {
                'primary_route': route_result,
                'alternative_routes': alternative_paths,
                'optimization': data.get('optimization', 'shortest'),
                'bike_capacity': data.get('bike_capacity', 20)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/route-planning/stations/<int:from_station_id>/to/<int:to_station_id>', methods=['GET'])
@jwt_required()
def calculate_simple_route(from_station_id, to_station_id):
    """计算两个站点间的路径"""
    try:
        # 验证站点存在
        from_station = Station.query.get_or_404(from_station_id)
        to_station = Station.query.get_or_404(to_station_id)

        # 获取A*规划器
        planner = get_astar_planner()

        # 计算路径
        route_result = planner.find_path(from_station_id, to_station_id)

        if not route_result['success']:
            return jsonify({
                'error': '无法找到有效路径',
                'details': route_result.get('error', '未知错误')
            }), 400

        # 添加站点信息
        route_result['from_station'] = from_station.to_dict()
        route_result['to_station'] = to_station.to_dict()

        # 获取路径统计信息
        if route_result['path']:
            route_result['statistics'] = planner.get_path_statistics(route_result['path'])

        return jsonify({
            'data': route_result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/route-planning/task/<int:task_id>', methods=['GET'])
@jwt_required()
def get_route_for_task(task_id):
    """获取调度任务的路径规划"""
    try:
        # 验证调度任务存在
        task = DispatchTask.query.get_or_404(task_id)

        # 查找关联的路径规划
        route_plan = RoutePlan.query.filter_by(task_id=task_id).first()

        if route_plan:
            return jsonify({
                'data': route_plan.to_dict()
            })
        else:
            # 如果没有路径规划，自动计算一个
            if task.from_station_id and task.to_station_id:
                planner = get_astar_planner()
                route_result = planner.find_path(task.from_station_id, task.to_station_id)

                if route_result['success']:
                    return jsonify({
                        'message': '未找到保存的路径规划，已生成临时路径',
                        'data': {
                            'task_id': task_id,
                            'calculated_route': route_result,
                            'from_station': task.from_station.to_dict() if task.from_station else None,
                            'to_station': task.to_station.to_dict() if task.to_station else None
                        }
                    })
                else:
                    return jsonify({
                        'error': '无法为该任务生成路径',
                        'details': route_result.get('error', '未知错误')
                    }), 400
            else:
                return jsonify({'error': '任务缺少起点或终点信息'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/route-planning/<int:id>/start', methods=['POST'])
@jwt_required()
def start_route_execution(id):
    """开始执行路径规划"""
    try:
        current_user_id = get_jwt_identity()
        route_plan = RoutePlan.query.get_or_404(id)

        # 验证权限
        if route_plan.created_by != current_user_id:
            return jsonify({'error': '权限不足'}), 403

        # 更新状态
        route_plan.status = 'in_progress'

        # 创建历史记录
        history = RouteHistory(
            route_plan_id=id,
            actual_start_time=datetime.utcnow(),
            completion_status='in_progress'
        )

        db.session.add(history)
        db.session.commit()

        return jsonify({
            'message': '路径执行已开始',
            'data': route_plan.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/route-planning/<int:id>/complete', methods=['POST'])
@jwt_required()
def complete_route_execution(id):
    """完成路径规划执行"""
    try:
        current_user_id = get_jwt_identity()
        route_plan = RoutePlan.query.get_or_404(id)
        data = request.get_json()

        # 验证权限
        if route_plan.created_by != current_user_id:
            return jsonify({'error': '权限不足'}), 403

        # 更新路径状态
        route_plan.status = 'completed'

        # 更新历史记录
        history = RouteHistory.query.filter_by(
            route_plan_id=id,
            completion_status='in_progress'
        ).first()

        if history:
            history.actual_end_time = datetime.utcnow()
            history.completion_status = 'success'
            history.actual_distance = data.get('actual_distance', route_plan.total_distance)
            history.actual_time = data.get('actual_time', route_plan.estimated_time)
            history.bikes_transported = data.get('bikes_transported', 0)
            history.notes = data.get('notes')
            history.driver_rating = data.get('driver_rating')
            history.route_difficulty = data.get('route_difficulty')
            history.traffic_conditions = data.get('traffic_conditions')
            history.feedback_notes = data.get('feedback_notes')
            history.issues_encountered = data.get('issues_encountered')

        db.session.commit()

        return jsonify({
            'message': '路径执行已完成',
            'data': route_plan.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/route-planning/statistics', methods=['GET'])
@jwt_required()
def get_route_statistics():
    """获取路径规划统计信息"""
    try:
        # 总体统计
        total_plans = RoutePlan.query.count()
        completed_plans = RoutePlan.query.filter_by(status='completed').count()
        in_progress_plans = RoutePlan.query.filter_by(status='in_progress').count()

        # 距离和时间统计
        avg_distance = db.session.query(db.func.avg(RoutePlan.total_distance)).scalar() or 0
        avg_time = db.session.query(db.func.avg(RoutePlan.estimated_time)).scalar() or 0

        # 算法使用统计
        algorithm_stats = db.session.query(
            RoutePlan.algorithm_used,
            db.func.count(RoutePlan.id).label('count')
        ).group_by(RoutePlan.algorithm_used).all()

        # 最常用的路径
        popular_routes = db.session.query(
            RoutePlan.start_station_id,
            RoutePlan.end_station_id,
            db.func.count(RoutePlan.id).label('usage_count')
        ).group_by(
            RoutePlan.start_station_id,
            RoutePlan.end_station_id
        ).order_by(db.func.count(RoutePlan.id).desc()).limit(5).all()

        return jsonify({
            'overview': {
                'total_plans': total_plans,
                'completed_plans': completed_plans,
                'in_progress_plans': in_progress_plans,
                'completion_rate': round(completed_plans / total_plans * 100, 2) if total_plans > 0 else 0
            },
            'performance': {
                'average_distance': round(avg_distance, 2),
                'average_time': round(avg_time, 2)
            },
            'algorithm_usage': [
                {
                    'algorithm': stat[0],
                    'usage_count': stat[1]
                } for stat in algorithm_stats
            ],
            'popular_routes': [
                {
                    'start_station_id': route[0],
                    'end_station_id': route[1],
                    'usage_count': route[2]
                } for route in popular_routes
            ]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500