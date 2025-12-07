from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 导入所有路由模块（chat.py中的路由会自动注册到api_bp）
from app.routes import stations, demand_data, users, dispatch_tasks, predictions, bike_history, route_planning, chat