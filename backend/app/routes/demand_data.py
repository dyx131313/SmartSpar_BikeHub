from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models.demand_data import DemandData
from app.models.station import Station
from app.routes import api_bp
from app.utils.permissions import require_role
import json


@api_bp.route("/demand-data", methods=["GET"])
@jwt_required()
@require_role("admin", "dispatcher")
def get_demand_data():
    """获取需求数据"""
    try:
        # 获取查询参数
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        station_type = request.args.get("station_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        weather = request.args.get("weather")
        weekday = request.args.get("weekday", type=int)

        # 构建查询
        query = DemandData.query

        if station_type:
            query = query.filter(DemandData.station_type == station_type)
        if start_date:
            query = query.filter(
                DemandData.timestamp >= datetime.fromisoformat(start_date)
            )
        if end_date:
            query = query.filter(
                DemandData.timestamp <= datetime.fromisoformat(end_date)
            )
        if weather:
            query = query.filter(DemandData.weather == weather)
        if weekday is not None:
            query = query.filter(DemandData.weekday == weekday)

        # 获取系统时间 (暂时硬编码，与 system_time 保持一致)
        system_time_str = "2025-12-08T00:00:00"
        system_time = datetime.fromisoformat(system_time_str)

        # 默认只显示系统时间之前的数据，除非显式指定了 end_date 且该 end_date 大于系统时间（通常不应该发生，除非查看未来计划）
        # 这里为了满足"实时需求展示系统时间之前的需求"的要求，强制或默认过滤
        if not end_date:
            query = query.filter(DemandData.timestamp <= system_time)
        elif end_date:
            # 如果用户传了 end_date，我们也限制它不能超过系统时间，或者就按用户传的来？
            # 既然是"实时需求"，理论上不应该看到未来的。
            # 但为了灵活性，如果用户传了 end_date，我们取 min(end_date, system_time)
            user_end_date = datetime.fromisoformat(end_date)
            final_end_date = min(user_end_date, system_time)
            query = query.filter(DemandData.timestamp <= final_end_date)

        # 分页查询
        pagination = query.order_by(DemandData.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify(
            {
                "data": [item.to_dict() for item in pagination.items],
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page,
                "per_page": per_page,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/demand-data", methods=["POST"])
@jwt_required()
@require_role("admin", "dispatcher", "user", "operator")
def create_demand_data():
    """创建需求数据"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "请求数据不能为空"}), 400

        # 批量创建或单个创建
        if isinstance(data, list):
            # 批量创建
            demand_items = []
            for item in data:
                demand_item = DemandData.create_from_json(item)
                # 如果提供了station_id，验证站点是否存在
                if "station_id" in item:
                    station = Station.query.get(item["station_id"])
                    if not station:
                        return (
                            jsonify({"error": f"站点ID {item['station_id']} 不存在"}),
                            400,
                        )
                    demand_item.station_id = item["station_id"]
                demand_items.append(demand_item)

            db.session.add_all(demand_items)
            db.session.commit()

            return (
                jsonify(
                    {
                        "message": f"成功创建 {len(demand_items)} 条需求数据",
                        "data": [item.to_dict() for item in demand_items],
                    }
                ),
                201,
            )
        else:
            # 单个创建
            demand_item = DemandData.create_from_json(data)

            # 如果提供了station_id，验证站点是否存在
            if "station_id" in data:
                station = Station.query.get(data["station_id"])
                if not station:
                    return (
                        jsonify({"error": f"站点ID {data['station_id']} 不存在"}),
                        400,
                    )
                demand_item.station_id = data["station_id"]

            db.session.add(demand_item)
            db.session.commit()

            return (
                jsonify({"message": "需求数据创建成功", "data": demand_item.to_dict()}),
                201,
            )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/demand-data/import", methods=["POST"])
@jwt_required()
@require_role("admin", "dispatcher")
def import_demand_data():
    """从JSON文件导入需求数据"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "没有上传文件"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "没有选择文件"}), 400

        if not file.filename.endswith(".json"):
            return jsonify({"error": "只支持JSON文件格式"}), 400

        # 读取JSON文件
        content = file.read().decode("utf-8")
        data = json.loads(content)

        # 批量导入数据
        imported_count = 0
        skipped_count = 0
        errors = []

        for item in data:
            try:
                demand_item = DemandData.create_from_json(item)
                db.session.add(demand_item)
                imported_count += 1
            except Exception as e:
                skipped_count += 1
                errors.append(
                    f"数据项 {item.get('timestamp', 'unknown')} 导入失败: {str(e)}"
                )

        db.session.commit()

        return jsonify(
            {
                "message": "数据导入完成",
                "imported_count": imported_count,
                "skipped_count": skipped_count,
                "errors": errors[:10],  # 只返回前10个错误
            }
        )

    except json.JSONDecodeError:
        return jsonify({"error": "JSON文件格式错误"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/demand-data/<int:id>", methods=["GET"])
@jwt_required()
@require_role("admin", "dispatcher")
def get_demand_data_by_id(id):
    """根据ID获取需求数据"""
    try:
        demand_item = DemandData.query.get_or_404(id)
        return jsonify({"data": demand_item.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/demand-data/<int:id>", methods=["PUT"])
@jwt_required()
@require_role("admin", "dispatcher")
def update_demand_data(id):
    """更新需求数据"""
    try:
        demand_item = DemandData.query.get_or_404(id)
        data = request.get_json()

        # 更新字段
        if "timestamp" in data:
            demand_item.timestamp = datetime.fromisoformat(data["timestamp"])
        if "station_id" in data:
            station = Station.query.get(data["station_id"])
            if not station:
                return jsonify({"error": f"站点ID {data['station_id']} 不存在"}), 400
            demand_item.station_id = data["station_id"]
        if "station_type" in data:
            demand_item.station_type = data["station_type"]
        if "weekday" in data:
            demand_item.weekday = data["weekday"]
        if "is_holiday" in data:
            demand_item.is_holiday = data["is_holiday"]
        if "weather" in data:
            demand_item.weather = data["weather"]
        if "temp" in data:
            demand_item.temp = data["temp"]
        if "demand" in data:
            demand_item.demand = data["demand"]

        db.session.commit()
        return jsonify({"message": "需求数据更新成功", "data": demand_item.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/demand-data/<int:id>", methods=["DELETE"])
@jwt_required()
@require_role("admin", "dispatcher")
def delete_demand_data(id):
    """删除需求数据"""
    try:
        demand_item = DemandData.query.get_or_404(id)
        db.session.delete(demand_item)
        db.session.commit()
        return jsonify({"message": "需求数据删除成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/demand-data/statistics", methods=["GET"])
@jwt_required()
@require_role("admin", "dispatcher")
def get_demand_statistics():
    """获取需求数据统计"""
    try:
        # 获取查询参数
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        station_type = request.args.get("station_type")

        # 构建基础查询
        query = DemandData.query

        if start_date:
            query = query.filter(
                DemandData.timestamp >= datetime.fromisoformat(start_date)
            )
        if end_date:
            query = query.filter(
                DemandData.timestamp <= datetime.fromisoformat(end_date)
            )
        if station_type:
            query = query.filter(DemandData.station_type == station_type)

        # 统计数据
        total_records = query.count()
        avg_demand = (
            db.session.query(db.func.avg(DemandData.demand))
            .filter(*query.statement.where_clause.clauses)
            .scalar()
            or 0
        )
        max_demand = (
            db.session.query(db.func.max(DemandData.demand))
            .filter(*query.statement.where_clause.clauses)
            .scalar()
            or 0
        )
        min_demand = (
            db.session.query(db.func.min(DemandData.demand))
            .filter(*query.statement.where_clause.clauses)
            .scalar()
            or 0
        )

        # 按站点类型统计
        station_type_stats = (
            db.session.query(
                DemandData.station_type,
                db.func.count(DemandData.id).label("count"),
                db.func.avg(DemandData.demand).label("avg_demand"),
            )
            .filter(*query.statement.where_clause.clauses)
            .group_by(DemandData.station_type)
            .all()
        )

        # 按天气统计
        weather_stats = (
            db.session.query(
                DemandData.weather,
                db.func.count(DemandData.id).label("count"),
                db.func.avg(DemandData.demand).label("avg_demand"),
            )
            .filter(*query.statement.where_clause.clauses)
            .group_by(DemandData.weather)
            .all()
        )

        return jsonify(
            {
                "total_records": total_records,
                "average_demand": float(avg_demand),
                "max_demand": max_demand,
                "min_demand": min_demand,
                "station_type_stats": [
                    {
                        "station_type": stat[0],
                        "count": stat[1],
                        "avg_demand": float(stat[2]),
                    }
                    for stat in station_type_stats
                ],
                "weather_stats": [
                    {"weather": stat[0], "count": stat[1], "avg_demand": float(stat[2])}
                    for stat in weather_stats
                ],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
