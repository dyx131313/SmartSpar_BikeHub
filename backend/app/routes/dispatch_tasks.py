from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.dispatch_task import DispatchTask
from app.models.station import Station
from app.models.bike_history import BikeHistory
from app.models.user import User
from app.routes import api_bp

@api_bp.route('/dispatch-tasks', methods=['GET'])
@jwt_required()
def get_dispatch_tasks():
    """获取调度任务列表"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        priority = request.args.get('priority', type=int)
        assigned_to = request.args.get('assigned_to', type=int)

        query = DispatchTask.query

        # 根据用户角色过滤任务
        if current_user.role == 'operator':
            # 运维员只能看到分配给自己的任务
            query = query.filter(DispatchTask.assigned_to == current_user_id)
        elif current_user.role == 'dispatcher':
            # 调度员可以看到自己创建的任务和分配给运维员的任务
            query = query.filter(
                (DispatchTask.created_by == current_user_id) |
                (DispatchTask.assigned_to != None)
            )
        # 管理员可以看到所有任务

        if status:
            query = query.filter(DispatchTask.status == status)
        if priority:
            query = query.filter(DispatchTask.priority == priority)
        if assigned_to:
            query = query.filter(DispatchTask.assigned_to == assigned_to)

        pagination = query.order_by(DispatchTask.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'data': [task.to_dict() for task in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dispatch-tasks', methods=['POST'])
@jwt_required()
def create_dispatch_task():
    """创建调度任务"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只有调度员和管理员可以创建任务
        if current_user.role not in ['dispatcher', 'admin']:
            return jsonify({'error': '权限不足'}), 403

        data = request.get_json()

        # 验证站点是否存在
        if data.get('from_station_id'):
            from_station = Station.query.get(data['from_station_id'])
            if not from_station:
                return jsonify({'error': '起点站点不存在'}), 400

        if data.get('to_station_id'):
            to_station = Station.query.get(data['to_station_id'])
            if not to_station:
                return jsonify({'error': '终点站点不存在'}), 400

        # 如果分配给运维员，验证运维员是否存在
        if data.get('assigned_to'):
            assignee = User.query.get(data['assigned_to'])
            if not assignee or assignee.role != 'operator':
                return jsonify({'error': '指定的运维员不存在'}), 400

        task = DispatchTask(
            task_name=data['task_name'],
            from_station_id=data.get('from_station_id'),
            to_station_id=data.get('to_station_id'),
            bike_count=data.get('bike_count', 0),
            priority=data.get('priority', 1),
            status='pending',
            assigned_to=data.get('assigned_to'),
            created_by=current_user_id
        )

        db.session.add(task)
        db.session.commit()

        return jsonify({
            'message': '调度任务创建成功',
            'data': task.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dispatch-tasks/<int:id>', methods=['GET'])
@jwt_required()
def get_dispatch_task(id):
    """获取单个调度任务"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        task = DispatchTask.query.get_or_404(id)

        # 检查权限
        if (current_user.role == 'operator' and task.assigned_to != current_user_id) or \
           (current_user.role == 'dispatcher' and task.created_by != current_user_id and task.assigned_to is None):
            return jsonify({'error': '权限不足'}), 403

        return jsonify({'data': task.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dispatch-tasks/<int:id>', methods=['PUT'])
@jwt_required()
def update_dispatch_task(id):
    """更新调度任务"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        task = DispatchTask.query.get_or_404(id)
        data = request.get_json()

        # 权限检查
        if current_user.role == 'operator':
            # 运维员只能更新任务状态
            if 'status' in data:
                if data['status'] not in ['in_progress', 'completed']:
                    return jsonify({'error': '运维员只能将任务更新为进行中或已完成'}), 400
                # 记录旧状态以便后续判断是否需要更新单车记录
                old_status = task.status
                task.status = data['status']
                new_status = task.status
                # 如果任务刚刚被标记为已完成，调整出/入站点的单车数量并创建 BikeHistory 记录
                if old_status != 'completed' and new_status == 'completed':
                    try:
                        bike_count = int(task.bike_count or 0)
                        now = datetime.utcnow()

                        # 出发站扣车
                        if task.from_station_id and bike_count > 0:
                            latest_from = (
                                BikeHistory.query.filter_by(station_id=task.from_station_id)
                                .order_by(BikeHistory.timestamp.desc())
                                .first()
                            )
                            from_available = latest_from.available_bikes if latest_from else 0
                            from_total = latest_from.total_bikes if latest_from else from_available
                            new_from_available = max(0, from_available - bike_count)

                            from_history = BikeHistory(
                                station_id=task.from_station_id,
                                timestamp=now,
                                available_bikes=new_from_available,
                                available_docks=(latest_from.available_docks if latest_from else 0),
                                total_bikes=from_total,
                                total_docks=(latest_from.total_docks if latest_from else 0),
                                is_station_active=(latest_from.is_station_active if latest_from else True),
                                last_report_time=now,
                            )
                            db.session.add(from_history)

                        # 到达站加车
                        if task.to_station_id and bike_count > 0:
                            latest_to = (
                                BikeHistory.query.filter_by(station_id=task.to_station_id)
                                .order_by(BikeHistory.timestamp.desc())
                                .first()
                            )
                            to_available = latest_to.available_bikes if latest_to else 0
                            to_total = latest_to.total_bikes if latest_to else to_available
                            new_to_available = to_available + bike_count

                            to_history = BikeHistory(
                                station_id=task.to_station_id,
                                timestamp=now,
                                available_bikes=new_to_available,
                                available_docks=(latest_to.available_docks if latest_to else 0),
                                total_bikes=to_total,
                                total_docks=(latest_to.total_docks if latest_to else 0),
                                is_station_active=(latest_to.is_station_active if latest_to else True),
                                last_report_time=now,
                            )
                            db.session.add(to_history)
                    except Exception as e:
                        db.session.rollback()
                        return jsonify({'error': f'更新单车记录失败: {str(e)}'}), 500
            else:
                return jsonify({'error': '权限不足'}), 403
        elif current_user.role in ['dispatcher', 'admin']:
            # 调度员和管理员可以更新所有字段
            if 'task_name' in data:
                task.task_name = data['task_name']
            if 'from_station_id' in data:
                if data['from_station_id']:
                    from_station = Station.query.get(data['from_station_id'])
                    if not from_station:
                        return jsonify({'error': '起点站点不存在'}), 400
                task.from_station_id = data['from_station_id']
            if 'to_station_id' in data:
                if data['to_station_id']:
                    to_station = Station.query.get(data['to_station_id'])
                    if not to_station:
                        return jsonify({'error': '终点站点不存在'}), 400
                task.to_station_id = data['to_station_id']
            if 'bike_count' in data:
                task.bike_count = data['bike_count']
            if 'priority' in data:
                task.priority = data['priority']
            if 'status' in data:
                task.status = data['status']
            if 'assigned_to' in data:
                if data['assigned_to']:
                    assignee = User.query.get(data['assigned_to'])
                    if not assignee or assignee.role != 'operator':
                        return jsonify({'error': '指定的运维员不存在'}), 400
                task.assigned_to = data['assigned_to']

        db.session.commit()
        return jsonify({
            'message': '调度任务更新成功',
            'data': task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dispatch-tasks/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_dispatch_task(id):
    """删除调度任务"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只有管理员和任务创建者可以删除任务
        task = DispatchTask.query.get_or_404(id)

        if current_user.role not in ['admin', 'dispatcher'] or \
           (current_user.role == 'dispatcher' and task.created_by != current_user_id):
            return jsonify({'error': '权限不足'}), 403

        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': '调度任务删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dispatch-tasks/<int:id>/assign', methods=['POST'])
@jwt_required()
def assign_dispatch_task(id):
    """分配调度任务"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只有调度员和管理员可以分配任务
        if current_user.role not in ['dispatcher', 'admin']:
            return jsonify({'error': '权限不足'}), 403

        task = DispatchTask.query.get_or_404(id)
        data = request.get_json()

        operator_id = data.get('operator_id')
        if not operator_id:
            return jsonify({'error': '运维员ID不能为空'}), 400

        operator = User.query.get(operator_id)
        if not operator or operator.role != 'operator':
            return jsonify({'error': '指定的运维员不存在'}), 400

        task.assigned_to = operator_id
        task.status = 'pending'  # 重置状态为待接收

        db.session.commit()
        return jsonify({
            'message': '任务分配成功',
            'data': task.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500