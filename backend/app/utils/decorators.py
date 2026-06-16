from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.exceptions import HTTPException

from app import db
from app.models.user import User


def with_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as exc:
            db.session.rollback()
            return jsonify({"error": str(exc)}), 400
        except PermissionError as exc:
            db.session.rollback()
            return jsonify({"error": str(exc) or "权限不足"}), 403
        except HTTPException as exc:
            db.session.rollback()
            return jsonify({"error": exc.description}), exc.code
        except Exception as exc:
            db.session.rollback()
            return jsonify({"error": str(exc)}), 500

    return wrapper


def require_roles(*roles):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({"error": "未提供认证令牌"}), 401

            user = User.query.get(int(user_id))
            if not user:
                return jsonify({"error": "用户不存在"}), 401
            if not user.is_active:
                return jsonify({"error": "账户已被禁用"}), 403
            if roles and user.role not in roles:
                return jsonify({"error": "权限不足"}), 403

            return func(current_user=user, *args, **kwargs)

        return wrapper

    return decorator


def require_admin(func):
    return require_roles("admin")(func)


def require_dispatcher_or_admin(func):
    return require_roles("dispatcher", "admin")(func)


def require_any_authenticated(func):
    return require_roles("admin", "dispatcher", "operator", "user")(func)
