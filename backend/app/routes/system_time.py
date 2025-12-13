from flask import jsonify
from app.routes import api_bp
from app.services.time_service import time_service


@api_bp.route("/system/time", methods=["GET"])
def get_system_time():
    """
    获取系统当前时间
    返回基于 TimeService 的动态时间
    """
    current_time = time_service.get_current_time_str()
    return jsonify(
        {
            "current_time": current_time,
            "timezone": "UTC+8",
            "mode": "dynamic",  # static or dynamic
        }
    )
