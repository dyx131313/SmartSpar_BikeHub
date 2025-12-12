import json
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.station import Station
from app.routes import api_bp
from app.utils.permissions import require_admin, require_any_role


@api_bp.route("/stations/import", methods=["POST"])
@jwt_required()
@require_admin()
def import_stations():
    """导入站点数据 (JSON)"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not file.filename.endswith(".json"):
            return jsonify({"error": "Only JSON files are allowed"}), 400

        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format"}), 400

        if not isinstance(data, list):
            return jsonify({"error": "JSON data must be a list of stations"}), 400

        count = 0
        for item in data:
            # 简单的校验
            if not all(
                k in item for k in ("name", "station_type", "latitude", "longitude")
            ):
                continue  # 或者报错

            # 检查是否存在 (根据ID或名称? 这里假设根据ID如果存在则更新，否则新建，或者根据名称)
            # 既然是导入，通常是批量新增或覆盖。
            # 如果 JSON 中有 ID，尝试更新；如果没有 ID，创建新的。

            station = None
            if "id" in item:
                station = Station.query.get(item["id"])

            if not station:
                # 尝试根据名称查找，避免重复?
                # 暂时简单处理：如果有ID且没找到，就用该ID创建（如果数据库允许自增ID插入）；
                # 或者忽略ID，直接创建新记录。
                # 为了兼容 api_stations.json，我们尽量保留 ID，或者如果 ID 冲突就更新。
                if "id" in item:
                    # 注意：通常自增主键不建议手动插入，但在导入数据恢复场景下可能需要。
                    # 这里为了安全，如果 ID 存在但数据库没记录，我们新建一个对象但不指定 ID (让数据库自增)，
                    # 或者如果用户希望完全一致，可以尝试指定 ID。
                    # 让我们采用：如果有 ID，尝试查找更新；没找到，就新建（忽略 JSON 中的 ID，让数据库生成新的，防止冲突）。
                    # 修正：用户可能希望导入的数据覆盖现有的。
                    pass

                station = Station()

            station.name = item["name"]
            station.station_type = item["station_type"]
            station.latitude = item["latitude"]
            station.longitude = item["longitude"]
            station.capacity = item.get("capacity", 20)
            station.description = item.get("description")

            db.session.add(station)
            count += 1

        db.session.commit()
        return jsonify({"message": f"Successfully imported {count} stations"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/stations", methods=["GET"])
@jwt_required()
@require_any_role()
def get_stations():
    """获取所有站点"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        # 后端允许通过 per_page=0 来表示返回全部记录（不分页）
        # 为避免滥用，仍然限制最大每页为 1000 当请求全量时
        max_per_page = 1000
        station_type = request.args.get("station_type")

        query = Station.query
        if station_type:
            query = query.filter(Station.station_type == station_type)

        # 如果 per_page <= 0，返回全部记录（不分页）
        if per_page <= 0:
            items = query.all()
            total = len(items)
            return jsonify(
                {
                    "data": [station.to_dict() for station in items],
                    "total": total,
                    "pages": 1,
                    "current_page": 1,
                    "per_page": total,
                }
            )

        per_page = min(per_page, max_per_page)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify(
            {
                "data": [station.to_dict() for station in pagination.items],
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page,
                "per_page": per_page,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/stations", methods=["POST"])
@jwt_required()
@require_admin()
def create_station():
    """创建站点"""
    try:
        data = request.get_json()

        station = Station(
            name=data["name"],
            station_type=data["station_type"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            capacity=data.get("capacity", 20),
            description=data.get("description"),
        )

        db.session.add(station)
        db.session.commit()

        return jsonify({"message": "站点创建成功", "data": station.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/stations/<int:id>", methods=["GET"])
@jwt_required()
@require_any_role()
def get_station(id):
    """获取单个站点"""
    try:
        station = Station.query.get_or_404(id)
        return jsonify({"data": station.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/stations/<int:id>", methods=["PUT"])
@jwt_required()
@require_admin()
def update_station(id):
    """更新站点"""
    try:
        station = Station.query.get_or_404(id)
        data = request.get_json()

        if "name" in data:
            station.name = data["name"]
        if "station_type" in data:
            station.station_type = data["station_type"]
        if "latitude" in data:
            station.latitude = data["latitude"]
        if "longitude" in data:
            station.longitude = data["longitude"]
        if "capacity" in data:
            station.capacity = data["capacity"]
        if "description" in data:
            station.description = data["description"]

        db.session.commit()
        return jsonify({"message": "站点更新成功", "data": station.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/stations/<int:id>", methods=["DELETE"])
@jwt_required()
@require_admin()
def delete_station(id):
    """删除站点"""
    try:
        station = Station.query.get_or_404(id)
        db.session.delete(station)
        db.session.commit()
        return jsonify({"message": "站点删除成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
