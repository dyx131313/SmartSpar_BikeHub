from flask import jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.station import Station
from app.models.bike_history import BikeHistory
from app.models.prediction import Prediction
from app.models.demand_data import DemandData
from app.routes import api_bp
from sqlalchemy import func


@api_bp.route("/dashboard/stations", methods=["GET"])
@jwt_required()
def get_dashboard_stations():
    """
    获取仪表盘所需的站点聚合数据：
    包含站点基本信息、最新单车数量、最新预测需求
    """
    try:
        # 1. 获取所有站点
        stations = Station.query.all()

        # 2. 获取每个站点最新的单车历史记录 (用于现存单车量)
        # 使用子查询找到每个站点最大的 id (假设 id 越大时间越新，或者用 timestamp)
        latest_history_subquery = (
            db.session.query(
                BikeHistory.station_id, func.max(BikeHistory.id).label("max_id")
            )
            .group_by(BikeHistory.station_id)
            .subquery()
        )

        latest_histories = (
            db.session.query(BikeHistory)
            .join(
                latest_history_subquery,
                BikeHistory.id == latest_history_subquery.c.max_id,
            )
            .all()
        )

        # 转为字典方便查找: {station_id: available_bikes}
        bikes_map = {h.station_id: h.available_bikes for h in latest_histories}

        # 3. 获取每个站点最新的预测记录 (用于 AI 热力需求)
        latest_prediction_subquery = (
            db.session.query(
                Prediction.station_id, func.max(Prediction.id).label("max_id")
            )
            .group_by(Prediction.station_id)
            .subquery()
        )

        latest_predictions = (
            db.session.query(Prediction)
            .join(
                latest_prediction_subquery,
                Prediction.id == latest_prediction_subquery.c.max_id,
            )
            .all()
        )

        # 转为字典: {station_id: predicted_demand}
        prediction_map = {p.station_id: p.predicted_demand for p in latest_predictions}

        # 4. 获取每个站点最新的真实需求记录 (用于补充热力图数据)
        # 当没有预测数据时，使用用户录入的真实需求数据
        latest_demand_subquery = (
            db.session.query(
                DemandData.station_id, func.max(DemandData.id).label("max_id")
            )
            .group_by(DemandData.station_id)
            .subquery()
        )

        latest_demands = (
            db.session.query(DemandData)
            .join(
                latest_demand_subquery,
                DemandData.id == latest_demand_subquery.c.max_id,
            )
            .all()
        )

        # 转为字典: {station_id: demand}
        real_demand_map = {d.station_id: d.demand for d in latest_demands}

        # 5. 组装数据
        result = []

        # 模拟数据开关 (如果为 True，则生成模拟数据覆盖真实数据)
        USE_MOCK_DATA = True

        import random

        for station in stations:
            station_data = station.to_dict()

            if USE_MOCK_DATA:
                # 模拟数据生成
                # 经度 121.214169 附近
                # 纬度 31.287779 附近
                # 需求量 20 附近

                # 简单的模拟逻辑：如果站点坐标在目标附近，给予较高的模拟值
                # 这里为了演示效果，直接给所有站点生成模拟数据，但会根据距离目标点的远近调整

                target_lat = 31.287779
                target_lng = 121.214169

                # 计算简单的距离因子 (非精确距离)
                lat_diff = abs(float(station.latitude) - target_lat)
                lng_diff = abs(float(station.longitude) - target_lng)

                # 如果在附近 (比如 0.01 度范围内)
                if lat_diff < 0.01 and lng_diff < 0.01:
                    base_demand = 20
                    variation = random.randint(-5, 10)
                    mock_demand = base_demand + variation
                else:
                    mock_demand = random.randint(0, 5)

                station_data["current_bikes"] = random.randint(0, 30)
                station_data["predicted_demand"] = mock_demand  # 模拟预测需求
                station_data["real_demand"] = mock_demand + random.randint(
                    -3, 3
                )  # 模拟真实需求

            else:
                # 真实数据逻辑
                station_data["current_bikes"] = bikes_map.get(station.id, 0)
                station_data["predicted_demand"] = prediction_map.get(station.id, 0)
                station_data["real_demand"] = real_demand_map.get(station.id, 0)

            result.append(station_data)

        return jsonify({"data": result, "count": len(result)})

    except Exception as e:
        print(f"Error in dashboard stations: {e}")
        return jsonify({"error": str(e)}), 500
