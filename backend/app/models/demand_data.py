from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db


class DemandData(db.Model):
    """需求数据模型"""

    __tablename__ = "demand_data"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, comment="时间戳")
    station_id = db.Column(
        db.Integer, db.ForeignKey("stations.id"), nullable=False, comment="站点ID"
    )
    station_type = db.Column(db.String(50), nullable=False, comment="站点类型")
    weekday = db.Column(db.Integer, nullable=False, comment="星期几(1-7)")
    is_holiday = db.Column(
        db.Integer, nullable=False, default=0, comment="是否节假日(0否,1是)"
    )
    weather = db.Column(db.String(20), nullable=False, comment="天气状况")
    temp = db.Column(db.Numeric(5, 2), nullable=False, comment="温度(摄氏度)")
    demand = db.Column(db.Integer, nullable=False, comment="需求数量")
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment="创建时间")

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "station_id": self.station_id,
            "station_type": self.station_type,
            "weekday": self.weekday,
            "is_holiday": bool(self.is_holiday),
            "weather": self.weather,
            "temp": float(self.temp),
            "demand": self.demand,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<DemandData {self.station_type} at {self.timestamp}>"

    @classmethod
    def create_from_json(cls, data_dict):
        """从JSON数据创建实例"""
        timestamp_str = data_dict["timestamp"]
        # 兼容处理：如果时间字符串以 Z 结尾（UTC），去掉 Z 以适配旧版 Python 的 fromisoformat
        if isinstance(timestamp_str, str) and timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str[:-1]

        return cls(
            timestamp=datetime.fromisoformat(timestamp_str),
            station_type=data_dict["station_type"],
            weekday=data_dict["weekday"],
            is_holiday=data_dict.get("is_holiday", 0),
            weather=data_dict["weather"],
            temp=data_dict["temp"],
            demand=data_dict["demand"],
        )
