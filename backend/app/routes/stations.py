from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.station import Station
from app.routes import api_bp

@api_bp.route('/stations', methods=['GET'])
@jwt_required()
def get_stations():
    """获取所有站点"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        station_type = request.args.get('station_type')

        query = Station.query
        if station_type:
            query = query.filter(Station.station_type == station_type)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'data': [station.to_dict() for station in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stations', methods=['POST'])
@jwt_required()
def create_station():
    """创建站点"""
    try:
        data = request.get_json()

        station = Station(
            name=data['name'],
            station_type=data['station_type'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            capacity=data.get('capacity', 20),
            description=data.get('description')
        )

        db.session.add(station)
        db.session.commit()

        return jsonify({
            'message': '站点创建成功',
            'data': station.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stations/<int:id>', methods=['GET'])
@jwt_required()
def get_station(id):
    """获取单个站点"""
    try:
        station = Station.query.get_or_404(id)
        return jsonify({'data': station.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stations/<int:id>', methods=['PUT'])
@jwt_required()
def update_station(id):
    """更新站点"""
    try:
        station = Station.query.get_or_404(id)
        data = request.get_json()

        if 'name' in data:
            station.name = data['name']
        if 'station_type' in data:
            station.station_type = data['station_type']
        if 'latitude' in data:
            station.latitude = data['latitude']
        if 'longitude' in data:
            station.longitude = data['longitude']
        if 'capacity' in data:
            station.capacity = data['capacity']
        if 'description' in data:
            station.description = data['description']

        db.session.commit()
        return jsonify({
            'message': '站点更新成功',
            'data': station.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stations/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_station(id):
    """删除站点"""
    try:
        station = Station.query.get_or_404(id)
        db.session.delete(station)
        db.session.commit()
        return jsonify({'message': '站点删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500