from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Alert(db.Model):
    """警报模型"""
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.Enum('low_bikes', 'full_station', 'system_error',
                                  'weather_warning', 'high_demand', name='alert_type'),
                           nullable=False, comment='警报类型')
    severity = db.Column(db.Enum('low', 'medium', 'high', 'critical', name='alert_severity'),
                        nullable=False, comment='严重程度')
    title = db.Column(db.String(100), nullable=False, comment='警报标题')
    message = db.Column(db.Text, nullable=False, comment='警报消息')
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), comment='相关站点ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='创建用户ID')
    status = db.Column(db.Enum('active', 'acknowledged', 'resolved', 'dismissed', name='alert_status'),
                       default='active', comment='警报状态')
    is_resolved = db.Column(db.Boolean, default=False, comment='是否已解决')
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='解决用户ID')
    resolved_at = db.Column(db.DateTime, comment='解决时间')
    resolution_notes = db.Column(db.Text, comment='解决备注')
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='确认用户ID')
    acknowledged_at = db.Column(db.DateTime, comment='确认时间')
    metadata = db.Column(db.JSON, comment='附加数据')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    station = db.relationship('Station', backref='alerts', lazy=True)
    creator = db.relationship('User', foreign_keys=[user_id], backref='created_alerts', lazy=True)
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_alerts', lazy=True)
    acknowledger = db.relationship('User', foreign_keys=[acknowledged_by], backref='acknowledged_alerts', lazy=True)

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'message': self.message,
            'station_id': self.station_id,
            'station': self.station.to_dict() if self.station else None,
            'user_id': self.user_id,
            'creator': self.creator.to_dict() if self.creator else None,
            'status': self.status,
            'is_resolved': self.is_resolved,
            'resolved_by': self.resolved_by,
            'resolver': self.resolver.to_dict() if self.resolver else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes,
            'acknowledged_by': self.acknowledged_by,
            'acknowledger': self.acknowledger.to_dict() if self.acknowledger else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Alert {self.alert_type} {self.severity}>'

class AlertSubscription(db.Model):
    """警报订阅模型"""
    __tablename__ = 'alert_subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    alert_type = db.Column(db.Enum('low_bikes', 'full_station', 'bike_maintenance', 'system_error',
                                  'weather_warning', 'high_demand', name='subscription_alert_type'),
                           nullable=False, comment='警报类型')
    severity_min = db.Column(db.Enum('low', 'medium', 'high', 'critical', name='min_severity'),
                            default='low', comment='最小严重程度')
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), comment='指定站点ID(为空表示所有站点)')
    notification_method = db.Column(db.Enum('email', 'sms', 'push', 'webhook', name='notification_method'),
                                   default='email', comment='通知方式')
    notification_address = db.Column(db.String(255), comment='通知地址')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    user = db.relationship('User', backref='alert_subscriptions', lazy=True)
    station = db.relationship('Station', backref='alert_subscriptions', lazy=True)

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'alert_type': self.alert_type,
            'severity_min': self.severity_min,
            'station_id': self.station_id,
            'station': self.station.to_dict() if self.station else None,
            'notification_method': self.notification_method,
            'notification_address': self.notification_address,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<AlertSubscription User {self.user_id} {self.alert_type}>'