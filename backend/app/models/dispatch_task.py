from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class DispatchTask(db.Model):
    """调度任务模型"""
    __tablename__ = 'dispatch_tasks'

    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(100), nullable=False, comment='任务名称')
    from_station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), comment='起点站点ID')
    to_station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), comment='终点站点ID')
    bike_count = db.Column(db.Integer, nullable=False, default=0, comment='调度单车数量')
    priority = db.Column(db.Integer, nullable=False, default=1, comment='优先级(1-5)')
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', 'cancelled', name='task_status'),
                       nullable=False, default='pending', comment='任务状态')
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), comment='分配给的运维员ID')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='创建者ID')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'task_name': self.task_name,
            'from_station_id': self.from_station_id,
            'to_station_id': self.to_station_id,
            'from_station': self.from_station.to_dict() if self.from_station else None,
            'to_station': self.to_station.to_dict() if self.to_station else None,
            'bike_count': self.bike_count,
            'priority': self.priority,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'assignee': self.assignee.to_dict() if self.assignee else None,
            'created_by': self.created_by,
            'creator': self.creator.to_dict() if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<DispatchTask {self.task_name}>'