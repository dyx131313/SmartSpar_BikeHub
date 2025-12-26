from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db

class Feedback(db.Model):
    """用户反馈与调度异常反馈模型"""
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='提交用户ID')
    category = db.Column(db.Enum('user_feedback', 'dispatcher_issue', name='feedback_category'), 
                         nullable=False, comment='反馈类型')
    title = db.Column(db.String(100), nullable=False, comment='标题')
    content = db.Column(db.Text, nullable=False, comment='内容')
    status = db.Column(db.Enum('pending', 'processing', 'resolved', 'closed', name='feedback_status'), 
                       default='pending', comment='状态')
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 处理结果
    resolution_notes = db.Column(db.Text, comment='处理备注')
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'), comment='处理人ID')
    resolved_at = db.Column(db.DateTime, comment='处理时间')

    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='feedbacks', lazy=True)
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_feedbacks', lazy=True)

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'category': self.category,
            'category_display': '用户反馈' if self.category == 'user_feedback' else '调度异常',
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'status_display': {
                'pending': '待处理',
                'processing': '处理中',
                'resolved': '已解决',
                'closed': '已关闭'
            }.get(self.status, self.status),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolution_notes': self.resolution_notes,
            'resolved_by': self.resolved_by,
            'resolver': self.resolver.to_dict() if self.resolver else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

    def __repr__(self):
        return f'<Feedback {self.id} {self.title}>'



