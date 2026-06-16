from flask import jsonify

from app.routes import api_bp
from app.services.dashboard_service import dashboard_service
from app.utils.decorators import require_any_authenticated, with_error_handler


@api_bp.route("/dashboard/stations", methods=["GET"])
@with_error_handler
@require_any_authenticated
def get_dashboard_stations(current_user):
    """获取仪表盘站点聚合数据"""
    data = dashboard_service.get_station_overview()
    return jsonify({"data": data, "count": len(data)})
