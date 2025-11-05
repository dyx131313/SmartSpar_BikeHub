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
    predicted_bikes_needed = db.Column(db.Integer, default=0, comment='预测需要的单车数量')
    confidence_score = db.Column(db.Numeric(5, 4), nullable=False, comment='置信度分数')
    model_version = db.Column(db.String(50), nullable=False, comment='模型版本')
    prediction_type = db.Column(db.Enum('demand', 'supply', 'dispatch', name='prediction_type'),
                               default='demand', comment='预测类型')
    weather_forecast = db.Column(db.String(20), comment='天气预报')
    temp_forecast = db.Column(db.Numeric(5, 2), comment='温度预报')
    is_holiday = db.Column(db.Boolean, default=False, comment='是否节假日')
    weekday = db.Column(db.Integer, comment='星期几(1-7)')
    actual_demand = db.Column(db.Integer, comment='实际需求(用于模型评估)')
    accuracy_score = db.Column(db.Numeric(5, 4), comment='预测准确度')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    station = db.relationship('Station', backref='predictions', lazy=True)

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'station_id': self.station_id,
            'station': self.station.to_dict() if self.station else None,
            'prediction_time': self.prediction_time.isoformat() if self.prediction_time else None,
            'predicted_demand': self.predicted_demand,
            'predicted_bikes_needed': self.predicted_bikes_needed,
            'confidence_score': float(self.confidence_score),
            'model_version': self.model_version,
            'prediction_type': self.prediction_type,
            'weather_forecast': self.weather_forecast,
            'temp_forecast': float(self.temp_forecast) if self.temp_forecast else None,
            'is_holiday': self.is_holiday,
            'weekday': self.weekday,
            'actual_demand': self.actual_demand,
            'accuracy_score': float(self.accuracy_score) if self.accuracy_score else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Prediction Station {self.station_id} at {self.prediction_time}>'

class PredictionModel(db.Model):
    """预测模型管理"""
    __tablename__ = 'prediction_models'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False, comment='模型名称')
    model_version = db.Column(db.String(50), nullable=False, comment='模型版本')
    model_type = db.Column(db.Enum('linear_regression', 'random_forest', 'neural_network', 'lstm',
                                  name='model_type'), nullable=False, comment='模型类型')
    model_parameters = db.Column(db.JSON, comment='模型参数')
    training_data_start = db.Column(db.DateTime, comment='训练数据开始时间')
    training_data_end = db.Column(db.DateTime, comment='训练数据结束时间')
    accuracy_metrics = db.Column(db.JSON, comment='准确度指标')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'model_type': self.model_type,
            'model_parameters': self.model_parameters,
            'training_data_start': self.training_data_start.isoformat() if self.training_data_start else None,
            'training_data_end': self.training_data_end.isoformat() if self.training_data_end else None,
            'accuracy_metrics': self.accuracy_metrics,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<PredictionModel {self.model_name} v{self.model_version}>'