from flask import jsonify
from app.routes import api_bp


@api_bp.route("/system/time", methods=["GET"])
def get_system_time():
    """
    获取系统当前时间
    目前返回固定时间：2025-12-08T00:00:00
    """
    # 模拟时间
    current_time = "2025-12-08T00:00:00"
    return jsonify(
        {
            "current_time": current_time,
            "timezone": "UTC+8",
            "mode": "static",  # static or dynamic
        }
    )
