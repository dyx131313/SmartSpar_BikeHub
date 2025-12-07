from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.feedback import Feedback
from app.models.user import User
from app.routes import api_bp

@api_bp.route('/feedback', methods=['POST'])
@jwt_required()
def create_feedback():
    """提交反馈"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        data = request.get_json()

        # 确定反馈类型
        category = 'user_feedback'
        if current_user.role == 'dispatcher':
            category = 'dispatcher_issue'
        elif current_user.role == 'admin':
            # 管理员也可以提交，默认为 user_feedback 或者允许前端指定
            category = data.get('category', 'user_feedback')

        feedback = Feedback(
            user_id=current_user_id,
            category=category,
            title=data.get('title'),
            content=data.get('content'),
            status='pending'
        )

        db.session.add(feedback)
        db.session.commit()

        return jsonify({
            'message': '反馈提交成功',
            'data': feedback.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/feedback', methods=['GET'])
@jwt_required()
def get_feedbacks():
    """获取反馈列表"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        category = request.args.get('category')

        query = Feedback.query

        # 权限控制
        if current_user.role != 'admin':
            # 非管理员只能看自己的反馈
            query = query.filter(Feedback.user_id == current_user_id)
        
        # 筛选
        if status:
            query = query.filter(Feedback.status == status)
        if category:
            query = query.filter(Feedback.category == category)

        pagination = query.order_by(Feedback.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'data': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/feedback/<int:id>', methods=['PUT'])
@jwt_required()
def update_feedback(id):
    """更新反馈（管理员处理）"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403

        feedback = Feedback.query.get_or_404(id)
        data = request.get_json()

        if 'status' in data:
            feedback.status = data['status']
        
        if 'resolution_notes' in data:
            feedback.resolution_notes = data['resolution_notes']
            feedback.resolved_by = current_user_id
            feedback.resolved_at = datetime.utcnow()
            if feedback.status == 'pending':
                feedback.status = 'resolved' # 如果未指定状态，自动标记为已解决

        db.session.commit()

        return jsonify({
            'message': '反馈更新成功',
            'data': feedback.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



