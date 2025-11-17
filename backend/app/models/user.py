from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from app import db

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(100), unique=True, nullable=False, comment='邮箱')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    role = db.Column(db.Enum('admin', 'dispatcher', 'operator', 'user', name='user_role'),
                     nullable=False, default='user', comment='用户角色')
    full_name = db.Column(db.String(100), comment='全名')
    phone = db.Column(db.String(20), comment='电话')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    email_verified = db.Column(db.Boolean, default=False, comment='邮箱是否验证')
    last_login = db.Column(db.TIMESTAMP, comment='最后登录时间')
    login_count = db.Column(db.Integer, default=0, comment='登录次数')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    created_tasks = db.relationship('DispatchTask', foreign_keys='DispatchTask.created_by', backref='creator', lazy=True)
    assigned_tasks = db.relationship('DispatchTask', foreign_keys='DispatchTask.assigned_to', backref='assignee', lazy=True)
    user_sessions = db.relationship('UserSession', backref='user', lazy=True, cascade='all, delete-orphan')
    user_logs = db.relationship('UserLog', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典格式（不包含敏感信息）"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'

class UserSession(db.Model):
    """用户会话模型"""
    __tablename__ = 'user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    session_token = db.Column(db.String(255), unique=True, nullable=False, comment='会话令牌')
    ip_address = db.Column(db.String(45), comment='IP地址')
    user_agent = db.Column(db.Text, comment='用户代理')
    is_active = db.Column(db.Boolean, default=True, comment='是否活跃')
    expires_at = db.Column(db.DateTime, nullable=False, comment='过期时间')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')
    last_activity = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='最后活动时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }

    def __repr__(self):
        return f'<UserSession User {self.user_id}>'

class UserLog(db.Model):
    """用户操作日志模型"""
    __tablename__ = 'user_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='用户ID')
    action = db.Column(db.String(50), nullable=False, comment='操作类型')
    resource_type = db.Column(db.String(50), comment='资源类型')
    resource_id = db.Column(db.Integer, comment='资源ID')
    description = db.Column(db.Text, comment='操作描述')
    ip_address = db.Column(db.String(45), comment='IP地址')
    user_agent = db.Column(db.Text, comment='用户代理')
    status = db.Column(db.Enum('success', 'failure', 'warning', name='log_status'),
                       default='success', comment='操作状态')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<UserLog {self.action} by User {self.user_id}>'