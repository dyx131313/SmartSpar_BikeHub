from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class RoutePlan(db.Model):
    """路径规划表"""
    __tablename__ = 'route_plans'

    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(100), nullable=False, comment='规划名称')
    start_station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False, comment='起点站点ID')
    end_station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False, comment='终点站点ID')

    # 路径信息
    path_data = db.Column(db.JSON, nullable=False, comment='路径数据JSON')
    total_distance = db.Column(db.Float, nullable=False, default=0, comment='总距离(米)')
    estimated_time = db.Column(db.Integer, nullable=False, default=0, comment='预估时间(分钟)')
    algorithm_used = db.Column(db.String(50), nullable=False, default='A*', comment='使用的算法')

    # 多点路径信息
    waypoints = db.Column(db.JSON, comment='途径点数据JSON')
    is_multi_point = db.Column(db.Boolean, default=False, comment='是否多点路径')

    # 业务信息
    task_id = db.Column(db.Integer, db.ForeignKey('dispatch_tasks.id'), comment='关联的调度任务ID')
    bike_capacity = db.Column(db.Integer, default=20, comment='单车容量')
    optimization_goal = db.Column(db.String(20), default='shortest', comment='优化目标(shortest/fastest/balanced)')

    # 状态信息
    status = db.Column(db.Enum('planned', 'in_progress', 'completed', 'cancelled', name='route_status'),
                       nullable=False, default='planned', comment='路径状态')
    priority = db.Column(db.Integer, default=1, comment='优先级(1-5)')

    # 创建信息
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建者ID')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    start_station = db.relationship('Station', foreign_keys=[start_station_id], backref='route_starts')
    end_station = db.relationship('Station', foreign_keys=[end_station_id], backref='route_ends')
    creator = db.relationship('User', backref='created_routes')
    dispatch_task = db.relationship('DispatchTask', backref='route_plan')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'plan_name': self.plan_name,
            'start_station_id': self.start_station_id,
            'end_station_id': self.end_station_id,
            'start_station': self.start_station.to_dict() if self.start_station else None,
            'end_station': self.end_station.to_dict() if self.end_station else None,
            'path_data': self.path_data,
            'total_distance': self.total_distance,
            'estimated_time': self.estimated_time,
            'algorithm_used': self.algorithm_used,
            'waypoints': self.waypoints,
            'is_multi_point': self.is_multi_point,
            'task_id': self.task_id,
            'bike_capacity': self.bike_capacity,
            'optimization_goal': self.optimization_goal,
            'status': self.status,
            'priority': self.priority,
            'created_by': self.created_by,
            'creator': self.creator.to_dict() if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<RoutePlan {self.plan_name}>'

class RouteHistory(db.Model):
    """路径历史记录表"""
    __tablename__ = 'route_history'

    id = db.Column(db.Integer, primary_key=True)
    route_plan_id = db.Column(db.Integer, db.ForeignKey('route_plans.id'), nullable=False, comment='路径规划ID')

    # 执行信息
    actual_start_time = db.Column(db.TIMESTAMP, comment='实际开始时间')
    actual_end_time = db.Column(db.TIMESTAMP, comment='实际结束时间')
    actual_distance = db.Column(db.Float, comment='实际距离(米)')
    actual_time = db.Column(db.Integer, comment='实际用时(分钟)')

    # 执行结果
    completion_status = db.Column(db.Enum('success', 'partial', 'failed', name='completion_status'),
                                  comment='完成状态')
    bikes_transported = db.Column(db.Integer, default=0, comment='实际运输单车数量')
    notes = db.Column(db.Text, comment='执行备注')

    # 评价信息
    driver_rating = db.Column(db.Integer, comment='驾驶员评分(1-5)')
    route_difficulty = db.Column(db.Integer, comment='路径难度评分(1-5)')
    traffic_conditions = db.Column(db.String(20), comment('traffic_conditions'))

    # 反馈信息
    feedback_notes = db.Column(db.Text, comment='反馈备注')
    issues_encountered = db.Column(db.JSON, comment='遇到的问题')

    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')

    # 关系
    route_plan = db.relationship('RoutePlan', backref='history_records')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'route_plan_id': self.route_plan_id,
            'actual_start_time': self.actual_start_time.isoformat() if self.actual_start_time else None,
            'actual_end_time': self.actual_end_time.isoformat() if self.actual_end_time else None,
            'actual_distance': self.actual_distance,
            'actual_time': self.actual_time,
            'completion_status': self.completion_status,
            'bikes_transported': self.bikes_transported,
            'notes': self.notes,
            'driver_rating': self.driver_rating,
            'route_difficulty': self.route_difficulty,
            'traffic_conditions': self.traffic_conditions,
            'feedback_notes': self.feedback_notes,
            'issues_encountered': self.issues_encountered,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<RouteHistory {self.id}>'