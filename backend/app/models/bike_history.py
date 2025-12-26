from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class BikeHistory(db.Model):
    """站点单车历史信息模型"""
    __tablename__ = 'bike_history'

    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False, comment='站点ID')
    timestamp = db.Column(db.DateTime, nullable=False, comment='记录时间')
    available_bikes = db.Column(db.Integer, nullable=False, default=0, comment='可用单车数量')
    available_docks = db.Column(db.Integer, nullable=False, default=0, comment='可用停车位数量')
    total_bikes = db.Column(db.Integer, nullable=False, default=0, comment='总单车数量')
    total_docks = db.Column(db.Integer, nullable=False, default=0, comment='总停车位数量')
    is_station_active = db.Column(db.Boolean, default=True, comment='站点是否激活')
    last_report_time = db.Column(db.DateTime, comment='最后上报时间')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')

    # 关系
    station = db.relationship('Station', backref='bike_history', lazy=True)

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'station_id': self.station_id,
            'station': self.station.to_dict() if self.station else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'available_bikes': self.available_bikes,
            'available_docks': self.available_docks,
            'total_bikes': self.total_bikes,
            'total_docks': self.total_docks,
            'is_station_active': self.is_station_active,
            'last_report_time': self.last_report_time.isoformat() if self.last_report_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<BikeHistory Station {self.station_id} at {self.timestamp}>'