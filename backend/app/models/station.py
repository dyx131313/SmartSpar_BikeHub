from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Station(db.Model):
    """站点信息模型"""
    __tablename__ = 'stations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='站点名称')
    station_type = db.Column(db.String(50), nullable=False, comment='站点类型')
    latitude = db.Column(db.Numeric(10, 8), nullable=False, comment='纬度')
    longitude = db.Column(db.Numeric(11, 8), nullable=False, comment='经度')
    capacity = db.Column(db.Integer, nullable=False, default=20, comment='站点容量')
    description = db.Column(db.Text, comment='站点描述')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    demand_data = db.relationship('DemandData', backref='station', lazy=True, cascade='all, delete-orphan')
    from_tasks = db.relationship('DispatchTask', foreign_keys='DispatchTask.from_station_id', backref='from_station', lazy=True)
    to_tasks = db.relationship('DispatchTask', foreign_keys='DispatchTask.to_station_id', backref='to_station', lazy=True)
    predictions = db.relationship('Prediction', backref='station', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'station_type': self.station_type,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'capacity': self.capacity,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Station {self.name}>'