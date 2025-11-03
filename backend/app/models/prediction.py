from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Prediction(db.Model):
    """预测结果模型"""
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False, comment='站点ID')
    prediction_time = db.Column(db.DateTime, nullable=False, comment='预测时间点')
    predicted_demand = db.Column(db.Integer, nullable=False, comment='预测需求')
    confidence_score = db.Column(db.Numeric(5, 4), nullable=False, comment='置信度分数')
    model_version = db.Column(db.String(50), nullable=False, comment='模型版本')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'station_id': self.station_id,
            'station': self.station.to_dict() if self.station else None,
            'prediction_time': self.prediction_time.isoformat() if self.prediction_time else None,
            'predicted_demand': self.predicted_demand,
            'confidence_score': float(self.confidence_score),
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Prediction Station {self.station_id} at {self.prediction_time}>'