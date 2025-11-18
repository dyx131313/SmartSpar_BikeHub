from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User


def require_role(*allowed_roles):
    """
    权限装饰器，限制只有特定角色的用户可以访问接口

    Args:
        *allowed_roles: 允许访问的角色列表

    使用示例:
        @require_role('admin', 'dispatcher')
        def some_endpoint():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                if not current_user_id:
                    return jsonify({'error': '未提供认证令牌'}), 401

                current_user = User.query.get(current_user_id)
                if not current_user:
                    return jsonify({'error': '用户不存在'}), 401

                if not current_user.is_active:
                    return jsonify({'error': '账户已被禁用'}), 403

                if current_user.role not in allowed_roles:
                    return jsonify({'error': '权限不足'}), 403

                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': f'权限验证失败: {str(e)}'}), 500

        return decorated_function
    return decorator


def require_admin():
    """仅管理员可访问"""
    return require_role('admin')


def require_dispatcher_or_admin():
    """调度员和管理员可访问"""
    return require_role('dispatcher', 'admin')


def require_operator_or_admin():
    """运维员和管理员可访问"""
    return require_role('operator', 'admin')


def require_operator_dispatcher_or_admin():
    """运维员、调度员和管理员可访问"""
    return require_role('operator', 'dispatcher', 'admin')


def require_dispatcher_operator():
    """调度员和运维员可访问"""
    return require_role('dispatcher', 'operator')


def require_any_role():
    """任何已认证用户可访问"""
    return require_role('admin', 'dispatcher', 'operator', 'user')


def get_current_user():
    """
    获取当前用户的辅助函数

    Returns:
        User: 当前用户对象
    """
    current_user_id = get_jwt_identity()
    return User.query.get(current_user_id) if current_user_id else None


def check_permission(user_role, required_roles):
    """
    检查用户权限的辅助函数

    Args:
        user_role: 用户角色
        required_roles: 需要的角色列表

    Returns:
        bool: 是否有权限
    """
    return user_role in required_roles