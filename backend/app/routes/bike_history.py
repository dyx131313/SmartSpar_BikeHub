from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models.bike_history import BikeHistory
from app.models.station import Station
from app.models.user import User

bike_history_bp = Blueprint('bike_history', __name__)

@bike_history_bp.route('/api/bike-history', methods=['GET'])
@jwt_required()
def get_bike_history():
    """获取单车历史数据"""
    try:
        # 获取查询参数
        station_id = request.args.get('station_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)

        # 构建查询
        query = BikeHistory.query

        # 按站点过滤
        if station_id:
            query = query.filter(BikeHistory.station_id == station_id)

        # 按时间范围过滤
        if start_date:
            start_datetime = datetime.fromisoformat(start_date)
            query = query.filter(BikeHistory.timestamp >= start_datetime)

        if end_date:
            end_datetime = datetime.fromisoformat(end_date)
            query = query.filter(BikeHistory.timestamp <= end_datetime)

        # 排序和分页
        query = query.order_by(BikeHistory.timestamp.desc())
        bike_history = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'bike_history': [history.to_dict() for history in bike_history.items],
            'total': bike_history.total,
            'pages': bike_history.pages,
            'current_page': page
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bike_history_bp.route('/api/bike-history', methods=['POST'])
@jwt_required()
def create_bike_history():
    """创建单车历史记录"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # 验证必需字段
        required_fields = ['station_id', 'timestamp', 'available_bikes', 'available_docks', 'total_bikes', 'total_docks']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # 验证站点是否存在
        station = Station.query.get(data['station_id'])
        if not station:
            return jsonify({'error': 'Station not found'}), 404

        # 创建单车历史记录
        bike_history = BikeHistory(
            station_id=data['station_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            available_bikes=data['available_bikes'],
            available_docks=data['available_docks'],
            total_bikes=data['total_bikes'],
            total_docks=data['total_docks'],
            is_station_active=data.get('is_station_active', True),
            last_report_time=datetime.fromisoformat(data['last_report_time']) if data.get('last_report_time') else None
        )

        db.session.add(bike_history)
        db.session.commit()

        return jsonify(bike_history.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bike_history_bp.route('/api/bike-history/<int:history_id>', methods=['GET'])
@jwt_required()
def get_bike_history_detail(history_id):
    """获取单车历史记录详情"""
    try:
        bike_history = BikeHistory.query.get_or_404(history_id)
        return jsonify(bike_history.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bike_history_bp.route('/api/bike-history/<int:history_id>', methods=['PUT'])
@jwt_required()
def update_bike_history(history_id):
    """更新单车历史记录"""
    try:
        current_user_id = get_jwt_identity()
        bike_history = BikeHistory.query.get_or_404(history_id)
        data = request.get_json()

        # 更新字段
        updatable_fields = ['available_bikes', 'available_docks', 'total_bikes', 'total_docks',
                          'is_station_active', 'last_report_time']

        for field in updatable_fields:
            if field in data:
                if field in ['last_report_time'] and data[field]:
                    setattr(bike_history, field, datetime.fromisoformat(data[field]))
                else:
                    setattr(bike_history, field, data[field])

        db.session.commit()

        return jsonify(bike_history.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bike_history_bp.route('/api/bike-history/<int:history_id>', methods=['DELETE'])
@jwt_required()
def delete_bike_history(history_id):
    """删除单车历史记录"""
    try:
        current_user_id = get_jwt_identity()
        bike_history = BikeHistory.query.get_or_404(history_id)

        db.session.delete(bike_history)
        db.session.commit()

        return jsonify({'message': 'Bike history record deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bike_history_bp.route('/api/bike-history/station/<int:station_id>/latest', methods=['GET'])
@jwt_required()
def get_latest_bike_history(station_id):
    """获取站点最新的单车历史记录"""
    try:
        # 验证站点是否存在
        station = Station.query.get_or_404(station_id)

        # 获取最新的记录
        latest_history = BikeHistory.query.filter_by(station_id=station_id)\
            .order_by(BikeHistory.timestamp.desc())\
            .first()

        if not latest_history:
            return jsonify({'message': 'No bike history found for this station'}), 404

        return jsonify(latest_history.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bike_history_bp.route('/api/bike-history/statistics', methods=['GET'])
@jwt_required()
def get_bike_history_statistics():
    """获取单车历史统计信息"""
    try:
        # 获取查询参数
        station_id = request.args.get('station_id', type=int)
        days = request.args.get('days', 7, type=int)

        # 计算时间范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # 构建查询
        query = db.session.query(
            BikeHistory.station_id,
            Station.name,
            db.func.avg(BikeHistory.available_bikes).label('avg_available_bikes'),
            db.func.min(BikeHistory.available_bikes).label('min_available_bikes'),
            db.func.max(BikeHistory.available_bikes).label('max_available_bikes'),
            db.func.count(BikeHistory.id).label('record_count')
        ).join(Station, BikeHistory.station_id == Station.id)\
         .filter(BikeHistory.timestamp >= start_date)\
         .filter(BikeHistory.timestamp <= end_date)

        # 按站点过滤
        if station_id:
            query = query.filter(BikeHistory.station_id == station_id)

        # 分组和执行
        statistics = query.group_by(BikeHistory.station_id, Station.name).all()

        result = []
        for stat in statistics:
            result.append({
                'station_id': stat.station_id,
                'station_name': stat.name,
                'avg_available_bikes': float(stat.avg_available_bikes),
                'min_available_bikes': stat.min_available_bikes,
                'max_available_bikes': stat.max_available_bikes,
                'record_count': stat.record_count
            })

        return jsonify({
            'statistics': result,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bike_history_bp.route('/api/bike-history/batch', methods=['POST'])
@jwt_required()
def batch_create_bike_history():
    """批量创建单车历史记录"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if 'records' not in data:
            return jsonify({'error': 'Missing records field'}), 400

        records = data['records']
        if not isinstance(records, list):
            return jsonify({'error': 'Records must be a list'}), 400

        created_records = []

        for record_data in records:
            # 验证必需字段
            required_fields = ['station_id', 'timestamp', 'available_bikes', 'available_docks', 'total_bikes', 'total_docks']
            for field in required_fields:
                if field not in record_data:
                    return jsonify({'error': f'Missing required field: {field} in record'}), 400

            # 验证站点是否存在
            station = Station.query.get(record_data['station_id'])
            if not station:
                return jsonify({'error': f'Station not found: {record_data["station_id"]}'}), 404

            # 创建单车历史记录
            bike_history = BikeHistory(
                station_id=record_data['station_id'],
                timestamp=datetime.fromisoformat(record_data['timestamp']),
                available_bikes=record_data['available_bikes'],
                available_docks=record_data['available_docks'],
                total_bikes=record_data['total_bikes'],
                total_docks=record_data['total_docks'],
                is_station_active=record_data.get('is_station_active', True),
                last_report_time=datetime.fromisoformat(record_data['last_report_time']) if record_data.get('last_report_time') else None
            )

            db.session.add(bike_history)
            created_records.append(bike_history)

        db.session.commit()

        return jsonify({
            'message': f'Successfully created {len(created_records)} bike history records',
            'records': [record.to_dict() for record in created_records]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500