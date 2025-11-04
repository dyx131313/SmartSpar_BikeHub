from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.routes import api_bp

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()

        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': '用户名和密码不能为空'}), 400

        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']) and user.is_active:
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict()
            })
        else:
            return jsonify({'error': '用户名或密码错误'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只有管理员可以查看所有用户
        if current_user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        role = request.args.get('role')

        query = User.query
        if role:
            query = query.filter(User.role == role)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'data': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """创建用户"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只有管理员可以创建用户
        if current_user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403

        data = request.get_json()

        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '用户名已存在'}), 400

        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '邮箱已存在'}), 400

        user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'user'),
            full_name=data.get('full_name'),
            phone=data.get('phone')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': '用户创建成功',
            'data': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """获取当前用户信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        return jsonify({'data': user.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    """更新用户信息"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只有管理员可以更新其他用户信息
        if current_user.role != 'admin' and current_user_id != id:
            return jsonify({'error': '权限不足'}), 403

        user = User.query.get_or_404(id)
        data = request.get_json()

        if 'email' in data and data['email'] != user.email:
            # 检查新邮箱是否已被使用
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': '邮箱已被使用'}), 400
            user.email = data['email']

        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'phone' in data:
            user.phone = data['phone']

        # 只有管理员可以修改角色和激活状态
        if current_user.role == 'admin':
            if 'role' in data:
                user.role = data['role']
            if 'is_active' in data:
                user.is_active = data['is_active']

        # 如果提供了新密码
        if 'password' in data and data['password']:
            user.set_password(data['password'])

        db.session.commit()
        return jsonify({
            'message': '用户信息更新成功',
            'data': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500