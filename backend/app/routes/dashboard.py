import os
import json
from datetime import datetime
from flask import jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.station import Station
from app.models.bike_history import BikeHistory
from app.models.prediction import Prediction
from app.models.demand_data import DemandData
from app.routes import api_bp
from sqlalchemy import func, and_


@api_bp.route("/dashboard/stations", methods=["GET"])
@jwt_required()
def get_dashboard_stations():
    """
    获取仪表盘所需的站点聚合数据：
    包含站点基本信息、最新单车数量、最新预测需求
    """
    try:
        # 获取系统时间 (暂时硬编码，与 system_time 保持一致)
        system_time_str = "2025-12-08T00:00:00"
        system_time = datetime.fromisoformat(system_time_str)

        # 1. 获取所有站点
        stations = Station.query.all()

        # 2. 获取每个站点最新的单车历史记录 (用于现存单车量)
        # 逻辑：获取 timestamp <= system_time 的最新一条记录
        latest_history_subquery = (
            db.session.query(
                BikeHistory.station_id, func.max(BikeHistory.timestamp).label("max_ts")
            )
            .filter(BikeHistory.timestamp <= system_time)
            .group_by(BikeHistory.station_id)
            .subquery()
        )

        latest_histories = (
            db.session.query(BikeHistory)
            .join(
                latest_history_subquery,
                and_(
                    BikeHistory.station_id == latest_history_subquery.c.station_id,
                    BikeHistory.timestamp == latest_history_subquery.c.max_ts,
                ),
            )
            .all()
        )

        # 转为字典方便查找: {station_id: available_bikes}
        bikes_map = {h.station_id: h.available_bikes for h in latest_histories}

        # 3. 获取每个站点最新的预测记录 (用于 AI 热力需求)
        # 逻辑：读取 JSON 文件，获取 timestamp > system_time 的最近一条预测
        base_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "services",
            "time_series",
            "checkpoints",
        )
        # 默认使用 DLinear 模型
        file_path = os.path.join(base_path, "DLinear_future.json")

        prediction_map = {}
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                # raw_data is list of {station_id: int, predictions: [{timestamp: str, demand: float}, ...]}
                for item in raw_data:
                    s_id = item["station_id"]
                    # 筛选出未来的预测
                    future_preds = []
                    for p in item["predictions"]:
                        # 处理可能带Z的时间字符串
                        ts_str = p["timestamp"]
                        if ts_str.endswith("Z"):
                            ts_str = ts_str[:-1]
                        p_time = datetime.fromisoformat(ts_str)

                        if p_time > system_time:
                            future_preds.append({"time": p_time, "demand": p["demand"]})

                    if future_preds:
                        # 按时间排序，取最近的一个
                        future_preds.sort(key=lambda x: x["time"])
                        prediction_map[s_id] = future_preds[0]["demand"]

        # 4. 获取每个站点最新的真实需求记录 (用于补充热力图数据)
        # 逻辑：获取 timestamp <= system_time 的最新一条记录
        latest_demand_subquery = (
            db.session.query(
                DemandData.station_id, func.max(DemandData.timestamp).label("max_ts")
            )
            .filter(DemandData.timestamp <= system_time)
            .group_by(DemandData.station_id)
            .subquery()
        )

        latest_demands = (
            db.session.query(DemandData)
            .join(
                latest_demand_subquery,
                and_(
                    DemandData.station_id == latest_demand_subquery.c.station_id,
                    DemandData.timestamp == latest_demand_subquery.c.max_ts,
                ),
            )
            .all()
        )

        # 转为字典: {station_id: demand}
        real_demand_map = {d.station_id: d.demand for d in latest_demands}

        # 5. 组装数据
        result = []

        for station in stations:
            station_data = station.to_dict()

            # 填充数据，如果不存在则默认为 0
            station_data["current_bikes"] = bikes_map.get(station.id, 0)
            station_data["predicted_demand"] = prediction_map.get(station.id, 0)
            station_data["real_demand"] = real_demand_map.get(station.id, 0)

            result.append(station_data)

        return jsonify({"data": result, "count": len(result)})

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
