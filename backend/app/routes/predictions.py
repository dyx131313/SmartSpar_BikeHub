import os
import json
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from app import db
from app.models.prediction import Prediction
from app.models.station import Station
from app.routes import api_bp
from app.services.prediction_registry import prediction_model_registry
from app.utils.permissions import require_dispatcher_or_admin
from app.services.demand_predictor import (
    get_demand_predictor,
    predict_demand_for_station,
)

STATION_TYPE_CODES = {
    "gate": 0,
    "teaching": 1,
    "dormitory": 2,
    "sports": 3,
    "transit": 3,
}

WEATHER_CODES = {
    "sunny": 0,
    "clear": 0,
    "cloudy": 1,
    "overcast": 1,
    "rainy": 2,
    "rain": 2,
    "snowy": 2,
}


@api_bp.route("/predictions/models", methods=["GET"])
@jwt_required()
def list_prediction_models():
    """List supported prediction models from the central registry."""
    return jsonify(
        {
            "data": [
                {
                    "name": spec.name,
                    "display_name": spec.display_name,
                    "family": spec.family,
                    "has_params": spec.params_path.exists(),
                    "has_future": spec.future_path.exists(),
                }
                for spec in prediction_model_registry.all()
            ]
        }
    )


def _coerce_ai_prediction_input(data):
    normalized = dict(data)
    station_type = normalized.get("station_type")
    weather = normalized.get("weather")

    if isinstance(station_type, str):
        normalized["station_type"] = STATION_TYPE_CODES.get(station_type.lower(), 0)
    if isinstance(weather, str):
        normalized["weather"] = WEATHER_CODES.get(weather.lower(), 0)

    normalized["temp"] = float(normalized["temp"])
    normalized["is_holiday"] = int(normalized["is_holiday"])
    normalized["weekday"] = int(normalized["weekday"])
    return normalized


@api_bp.route("/predictions/models/<model_name>/params", methods=["GET"])
@jwt_required()
def get_model_params(model_name):
    """获取模型参数"""
    try:
        model = prediction_model_registry.require(model_name)
        file_path = model.params_path

        if not file_path.exists():
            return (
                jsonify({"error": "Model parameters not found", "exists": False}),
                404,
            )

        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return jsonify({"data": data, "exists": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/predictions/models/<model_name>/future", methods=["GET"])
@api_bp.route("/predictions/models/<model_name>/future_data", methods=["GET"])
@jwt_required()
def get_model_future(model_name):
    """获取模型预测的未来需求"""
    try:
        model = prediction_model_registry.require(model_name)
        # 获取查询参数
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        station_type_filter = request.args.get("station_type")
        if station_type_filter == "undefined":
            station_type_filter = None

        # 获取系统时间
        from app.services.time_service import time_service

        system_time = time_service.get_current_time()

        file_path = model.future_path

        if not file_path.exists():
            return (
                jsonify(
                    {
                        "data": [],
                        "total": 0,
                        "pages": 0,
                        "current_page": page,
                        "per_page": per_page,
                        "message": f"File not found: {file_path}",
                    }
                ),
                200,
            )

        with file_path.open("r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # 获取所有站点类型映射
        stations = Station.query.all()
        station_type_map = {s.id: s.station_type for s in stations}
        station_name_map = {s.id: s.name for s in stations}

        all_results = []
        archived_results = []
        for item in raw_data:
            station_id = item["station_id"]
            station_type = station_type_map.get(station_id, "Unknown")
            station_name = station_name_map.get(station_id, "Unknown")

            # 站点类型筛选
            if station_type_filter and station_type != station_type_filter:
                continue

            for pred in item["predictions"]:
                pred_time = datetime.fromisoformat(pred["timestamp"])
                result = {
                    "id": f"{model_name}-{station_id}-{pred['timestamp']}",
                    "time": pred["timestamp"],
                    "station_id": station_id,
                    "station_name": station_name,
                    "station_type": station_type,
                    "demand": pred["demand"],
                }
                archived_results.append(result)
                if pred_time > system_time:
                    all_results.append(result)

        data_source = "future"
        if not all_results and archived_results:
            all_results = archived_results
            data_source = "archived"

        # 排序：时间升序，站点ID升序
        all_results.sort(key=lambda x: (x["time"], x["station_id"]))

        # 分页处理
        total = len(all_results)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = all_results[start:end]
        pages = (total + per_page - 1) // per_page

        return jsonify(
            {
                "data": paginated_data,
                "total": total,
                "pages": pages,
                "current_page": page,
                "per_page": per_page,
                "data_source": data_source,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/predictions", methods=["GET"])
@jwt_required()
@require_dispatcher_or_admin()
def get_predictions():
    """获取预测结果"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        station_id = request.args.get("station_id", type=int)
        start_time = request.args.get("start_time")
        end_time = request.args.get("end_time")

        query = Prediction.query

        if station_id:
            query = query.filter(Prediction.station_id == station_id)
        if start_time:
            query = query.filter(
                Prediction.prediction_time >= datetime.fromisoformat(start_time)
            )
        if end_time:
            query = query.filter(
                Prediction.prediction_time <= datetime.fromisoformat(end_time)
            )

        pagination = query.order_by(Prediction.prediction_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify(
            {
                "data": [prediction.to_dict() for prediction in pagination.items],
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page,
                "per_page": per_page,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/predictions", methods=["POST"])
@jwt_required()
@require_dispatcher_or_admin()
def create_prediction():
    """创建预测结果"""
    try:
        data = request.get_json()

        # 验证站点是否存在
        station = Station.query.get(data["station_id"])
        if not station:
            return jsonify({"error": "站点不存在"}), 400

        prediction = Prediction(
            station_id=data["station_id"],
            prediction_time=datetime.fromisoformat(data["prediction_time"]),
            predicted_demand=data["predicted_demand"],
            confidence_score=data["confidence_score"],
            model_version=data.get("model_version", "v1.0"),
        )

        db.session.add(prediction)
        db.session.commit()

        return (
            jsonify({"message": "预测结果创建成功", "data": prediction.to_dict()}),
            201,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/predictions/station/<int:station_id>", methods=["GET"])
@jwt_required()
@require_dispatcher_or_admin()
def get_station_predictions(station_id):
    """获取特定站点的预测结果"""
    try:
        # 验证站点是否存在
        station = Station.query.get_or_404(station_id)

        # 获取查询参数
        hours_ahead = request.args.get("hours_ahead", 24, type=int)
        limit = request.args.get("limit", 100, type=int)

        # 获取未来几小时的预测
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=hours_ahead)

        predictions = (
            Prediction.query.filter(
                Prediction.station_id == station_id,
                Prediction.prediction_time >= start_time,
                Prediction.prediction_time <= end_time,
            )
            .order_by(Prediction.prediction_time)
            .limit(limit)
            .all()
        )

        return jsonify(
            {
                "station": station.to_dict(),
                "predictions": [prediction.to_dict() for prediction in predictions],
                "total": len(predictions),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/predictions/dashboard", methods=["GET"])
@jwt_required()
@require_dispatcher_or_admin()
def get_prediction_dashboard():
    """获取预测看板数据"""
    try:
        # 获取未来24小时的预测数据
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=24)

        # 获取所有站点的最新预测
        latest_predictions = (
            db.session.query(
                Prediction.station_id,
                db.func.max(Prediction.prediction_time).label("latest_time"),
            )
            .filter(Prediction.prediction_time.between(start_time, end_time))
            .group_by(Prediction.station_id)
            .subquery()
        )

        predictions = (
            db.session.query(Prediction, Station)
            .join(Station, Prediction.station_id == Station.id)
            .join(
                latest_predictions,
                (Prediction.station_id == latest_predictions.c.station_id)
                & (Prediction.prediction_time == latest_predictions.c.latest_time),
            )
            .all()
        )

        dashboard_data = []
        for prediction, station in predictions:
            dashboard_data.append(
                {"station": station.to_dict(), "prediction": prediction.to_dict()}
            )

        # 统计信息
        total_stations = len(dashboard_data)
        high_demand_stations = len(
            [p for p in dashboard_data if p["prediction"]["predicted_demand"] > 20]
        )
        avg_confidence = (
            sum(p["prediction"]["confidence_score"] for p in dashboard_data)
            / total_stations
            if total_stations > 0
            else 0
        )

        return jsonify(
            {
                "summary": {
                    "total_stations": total_stations,
                    "high_demand_stations": high_demand_stations,
                    "avg_confidence": round(avg_confidence, 4),
                },
                "data": dashboard_data,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/predictions/ai", methods=["POST"])
@jwt_required()
@require_dispatcher_or_admin()
def ai_predict_demand():
    """使用AI模型进行需求预测"""
    try:
        data = request.get_json()

        # 验证必需字段
        required_fields = [
            "station_type",
            "temp",
            "is_holiday",
            "weather",
            "weekday",
            "date",
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必需字段: {field}"}), 400

        # 调用AI预测服务
        try:
            normalized_data = _coerce_ai_prediction_input(data)
            prediction_result = predict_demand_for_station(
                station_type=normalized_data["station_type"],
                temp=normalized_data["temp"],
                is_holiday=normalized_data["is_holiday"],
                weather=normalized_data["weather"],
                weekday=normalized_data["weekday"],
                date_str=normalized_data["date"],
            )

            return jsonify(
                {
                    "success": True,
                    "prediction": prediction_result,
                    "input": data,
                    "normalized_input": normalized_data,
                    "message": "AI预测成功",
                }
            )

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"AI预测失败: {str(e)}",
                        "message": "预测服务暂时不可用",
                    }
                ),
                500,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/predictions/ai/batch", methods=["POST"])
@jwt_required()
@require_dispatcher_or_admin()
def ai_predict_batch():
    """批量AI需求预测"""
    try:
        data = request.get_json()

        if "predictions" not in data or not isinstance(data["predictions"], list):
            return jsonify({"error": "请求格式错误，需要predictions数组"}), 400

        input_data_list = [
            _coerce_ai_prediction_input(item) for item in data["predictions"]
        ]
        predictor = get_demand_predictor()

        try:
            batch_results = predictor.predict_batch(input_data_list)

            return jsonify(
                {
                    "success": True,
                    "results": batch_results,
                    "total": len(batch_results),
                    "successful": len(batch_results),
                    "failed": 0,
                    "message": "批量AI预测成功",
                }
            )

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"批量AI预测失败: {str(e)}",
                        "message": "预测服务暂时不可用",
                    }
                ),
                500,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/predictions/ai/model/info", methods=["GET"])
@jwt_required()
@require_dispatcher_or_admin()
def get_ai_model_info():
    """获取AI模型信息"""
    try:
        predictor = get_demand_predictor()
        model_info = predictor.get_model_info()

        return jsonify({"success": True, "model_info": model_info})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/predictions/ai/model/retrain", methods=["POST"])
@jwt_required()
@require_dispatcher_or_admin()
def retrain_ai_model():
    """重新训练AI模型"""
    try:
        predictor = get_demand_predictor()

        # 检查训练数据文件是否存在
        train_data_path = "train.csv"
        if not os.path.exists(train_data_path):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "训练数据文件不存在",
                        "message": f"请确保 {train_data_path} 文件存在",
                    }
                ),
                400,
            )

        # 重新训练模型
        training_results = predictor.train(train_data_path)

        return jsonify(
            {
                "success": True,
                "message": "AI模型重新训练完成",
                "training_results": training_results,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"重新训练失败: {str(e)}",
                    "message": "模型重新训练过程中出现错误",
                }
            ),
            500,
        )


@api_bp.route("/predictions/run", methods=["POST"])
@jwt_required()
@require_dispatcher_or_admin()
def run_prediction():
    """手动触发预测"""
    try:
        data = request.get_json()
        model_name = data.get("model_name")
        target_time_str = data.get("target_time")

        if not model_name:
            return jsonify({"error": "Model name is required"}), 400

        # 获取系统时间或使用指定时间
        from app.services.time_service import time_service

        if target_time_str:
            try:
                target_time = datetime.fromisoformat(target_time_str)
            except ValueError:
                return jsonify({"error": "Invalid time format"}), 400
        else:
            target_time = time_service.get_current_time()

        # 调用调度器运行预测
        from app.services.scheduler import scheduler

        # 在新线程中运行以避免阻塞请求
        import threading

        thread = threading.Thread(
            target=scheduler.run_prediction_cycle, args=(target_time, model_name)
        )
        thread.start()

        return jsonify(
            {
                "message": f"Prediction started for {model_name} at {target_time}",
                "status": "started",
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/predictions/status/<model_name>", methods=["GET"])
@jwt_required()
def get_prediction_status(model_name):
    """获取预测任务状态"""
    from app.services.scheduler import scheduler

    status = scheduler.prediction_status.get(
        model_name, {"status": "idle", "progress": 0, "message": "Idle"}
    )
    return jsonify(status)
