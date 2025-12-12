from flask import jsonify
from app.routes import api_bp
from datetime import datetime


@api_bp.route("/system/time", methods=["GET"])
def get_system_time():
    """
    获取系统当前时间（动态返回 UTC 当前时间）
    """
    current_time = datetime.utcnow().isoformat()
    return jsonify(
        {
            "current_time": current_time,
            "timezone": "UTC",
            "mode": "dynamic",
        }
    )
