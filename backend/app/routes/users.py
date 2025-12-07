from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from datetime import datetime
import re
import random
from sqlalchemy import or_
from app import db
from app.models.user import User
from app.models.verification_code import VerificationCode
from app.routes import api_bp
from app.utils.email_utils import send_verification_email


@api_bp.route("/auth/register", methods=["POST"])
def register():
    """User registration"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["username", "email", "password"]
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        # Validate username format
        username = data["username"].strip()
        if len(username) < 3 or len(username) > 20:
            return jsonify({"error": "Username length must be between 3 and 20 characters"}), 400
        if not username.replace("_", "").replace("-", "").isalnum():
            return jsonify({"error": "Username may only contain letters, numbers, underscore and hyphen"}), 400

        # Validate password strength (length only for now)
        password = data["password"]
        if len(password) < 6:
            return jsonify({"error": "Password length must be at least 6 characters"}), 400

        # Validate email format (allow any valid email domain)
        email = data["email"].strip().lower()
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return jsonify({"error": "Invalid email format"}), 400

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email has already been registered"}), 400

        # Create new user with default role 'user'
        user = User(
            username=username,
            email=email,
            role="user",
            full_name=data.get("full_name", "").strip(),
            phone=data.get("phone", "").strip(),
            is_active=True,
            # Currently we treat email as verified on registration
            email_verified=True,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(identity=str(user.id))

        return (
            jsonify(
                {
                    "message": "Register success",
                    "access_token": access_token,
                    "user": user.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Register failed: {str(e)}"}), 500


@api_bp.route("/auth/login", methods=["POST"])
def login():
    """User login (supports username or email + password)"""
    try:
        data = request.get_json() or {}

        identifier = (data.get("username") or data.get("email") or data.get("identifier") or "").strip()
        password = data.get("password")

        if not identifier or not password:
            return jsonify({"error": "Username or email and password are required"}), 400

        # Support login by username OR email
        user = (
            User.query.filter(
                or_(User.username == identifier, User.email == identifier)
            )
            .first()
        )

        if user and user.check_password(password) and user.is_active:
            access_token = create_access_token(identity=str(user.id))
            return jsonify({"access_token": access_token, "user": user.to_dict()})
        else:
            return jsonify({"error": "Invalid username/email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/auth/email/send-bind-code", methods=["POST"])
@jwt_required()
def send_bind_email_code():
    """Send verification code for binding email"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify({"error": "User does not exist or is disabled"}), 404

        data = request.get_json() or {}
        email = (data.get("email") or "").strip().lower()

        if not email:
            return jsonify({"error": "Email is required"}), 400

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return jsonify({"error": "Invalid email format"}), 400

        # Ensure the new email is not already used by another account
        exists = (
            User.query.filter(User.email == email, User.id != current_user_id)
            .first()
        )
        if exists:
            return jsonify({"error": "This email is already used by another account"}), 400

        code = f"{random.randint(0, 999999):06d}"
        verification = VerificationCode(
            email=email,
            code=code,
            type="bind_email",
        )
        db.session.add(verification)
        db.session.commit()

        subject = "BikeHub - Email binding verification code"
        body = (
            f"Your email binding verification code is: {code}\n\n"
            f"This code will expire in 10 minutes. If you did not request this, please ignore this email."
        )

        if not send_verification_email(email, subject, body):
            return jsonify({"error": "Failed to send verification email, please try again later"}), 500

        return jsonify({"message": "Verification code has been sent to the specified email"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/auth/email/verify-bind", methods=["POST"])
@jwt_required()
def verify_bind_email():
    """Verify email binding code and update user's email"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify({"error": "User does not exist or is disabled"}), 404

        data = request.get_json() or {}
        email = (data.get("email") or "").strip().lower()
        code = (data.get("code") or "").strip()

        if not email or not code:
            return jsonify({"error": "Email and verification code are required"}), 400

        verification = (
            VerificationCode.query.filter_by(
                email=email, type="bind_email", code=code, is_used=False
            )
            .order_by(VerificationCode.created_at.desc())
            .first()
        )

        if not verification or not verification.is_valid:
            return jsonify({"error": "Invalid or expired verification code"}), 400

        verification.is_used = True

        # Update user email
        user.email = email
        user.email_verified = True

        db.session.commit()

        return jsonify({"message": "Email binding successfully updated", "user": user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/auth/forgot-password/request", methods=["POST"])
def forgot_password_request():
    """Forgot password: send reset code to bound email (if any)"""
    try:
        data = request.get_json() or {}
        identifier = (data.get("identifier") or "").strip()

        if not identifier:
            return jsonify({"error": "Username or email is required"}), 400

        user = (
            User.query.filter(
                or_(User.username == identifier, User.email == identifier)
            )
            .first()
        )

        if not user:
            # Do not reveal whether the account exists
            return jsonify(
                {
                    "message": "If the account exists and has a bound email, a verification code will be sent"
                }
            )

        if not user.email:
            return jsonify({"error": "No email address is bound to this account, password cannot be reset"},), 400

        code = f"{random.randint(0, 999999):06d}"
        verification = VerificationCode(
            email=user.email,
            code=code,
            type="reset_password",
        )
        db.session.add(verification)
        db.session.commit()

        subject = "BikeHub - Password reset verification code"
        body = (
            f" 你的“重置密码”验证码是：{code}\n\n"
            f" 该验证码将在1分钟后过期，请尽快使用。如果您未请求重置密码，请忽略此邮件。"
        )

        if not send_verification_email(user.email, subject, body):
            return jsonify({"error": "Failed to send password reset email, please try again later"}), 500

        return jsonify(
            {
                "message": "If the account exists and has a bound email, a verification code has been sent to that email"
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/auth/forgot-password/reset", methods=["POST"])
def forgot_password_reset():
    """Forgot password: verify code and reset password"""
    try:
        data = request.get_json() or {}
        identifier = (data.get("identifier") or "").strip()
        code = (data.get("code") or "").strip()
        new_password = data.get("new_password") or ""

        if not identifier or not code or not new_password:
            return jsonify({"error": "Account identifier, verification code and new password are required"}), 400

        if len(new_password) < 6:
            return jsonify({"error": "New password length must be at least 6 characters"}), 400

        user = (
            User.query.filter(
                or_(User.username == identifier, User.email == identifier)
            )
            .first()
        )

        if not user or not user.email:
            return jsonify({"error": "Invalid verification code or account email not found"}), 400

        verification = (
            VerificationCode.query.filter_by(
                email=user.email, type="reset_password", code=code, is_used=False
            )
            .order_by(VerificationCode.created_at.desc())
            .first()
        )

        if not verification or not verification.is_valid:
            return jsonify({"error": "Invalid or expired verification code"}), 400

        verification.is_used = True
        user.set_password(new_password)

        db.session.commit()

        return jsonify({"message": "Password has been reset successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    """User logout (JWT token handled on client side)"""
    try:
        current_user_id = get_jwt_identity()
        jti = get_jwt()["jti"]  # JWT ID, could be stored in a blacklist in real deployments

        # Here we simply return success; the client should delete its local token.

        # Optionally update user's last login / logout time
        user = User.query.get(current_user_id)
        if user:
            # Could record logout info in logs if needed
            pass

        return jsonify(
            {"message": "Logout success", "logout_time": datetime.now().isoformat()}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify({"error": "用户不存在或已被禁用"}), 401

        # 创建新的访问令牌
        new_token = create_access_token(identity=str(user.id))

        return jsonify({"access_token": new_token, "user": user.to_dict()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """获取当前登录用户信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "用户不存�?"}), 404

        return jsonify({"data": user.to_dict()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    """获取用户列表"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只有管理员可以查看所有用�?
        if current_user.role != "admin":
            return jsonify({"error": "权限不足"}), 403

        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        role = request.args.get("role")

        query = User.query
        if role:
            query = query.filter(User.role == role)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify(
            {
                "data": [user.to_dict() for user in pagination.items],
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/users", methods=["POST"])
@jwt_required()
def create_user():
    """创建用户"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只有管理员可以创建用�?
        if current_user.role != "admin":
            return jsonify({"error": "权限不足"}), 403

        data = request.get_json()

        # 检查用户名是否已存�?
        if User.query.filter_by(username=data["username"]).first():
            return jsonify({"error": "用户名已存在"}), 400

        # 检查邮箱是否已存在
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "邮箱已存�?"}), 400

        user = User(
            username=data["username"],
            email=data["email"],
            role=data.get("role", "user"),
            full_name=data.get("full_name"),
            phone=data.get("phone"),
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "用户创建成功", "data": user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/users/profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    """获取当前用户信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "用户不存�?"}), 404

        return jsonify({"data": user.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/auth/debug-headers", methods=["GET", "POST"])
def debug_headers():
    """调试请求�? - 不验证JWT"""
    from flask import request

    auth_header = request.headers.get("Authorization", "")
    headers_dict = dict(request.headers)

    return jsonify(
        {
            "message": "请求头调试信�?",
            "auth_header": auth_header,
            "auth_header_type": type(auth_header).__name__,
            "auth_header_length": len(auth_header) if auth_header else 0,
            "has_bearer": auth_header.startswith("Bearer ") if auth_header else False,
            "raw_headers": {
                k: v for k, v in headers_dict.items() if k.lower() != "authorization"
            },
            "authorization_exists": "Authorization" in headers_dict,
            "authorization_value": (
                auth_header[:50] + "..." if len(auth_header) > 50 else auth_header
            ),
        }
    )


@api_bp.route("/auth/test", methods=["GET"])
@jwt_required()
def test_jwt():
    """测试JWT验证 - 用于调试"""
    try:
        current_user_id = get_jwt_identity()
        from flask_jwt_extended import get_jwt

        jwt_data = get_jwt()

        return jsonify(
            {
                "message": "JWT验证成功",
                "user_id": current_user_id,
                "jwt_data": jwt_data,
                "timestamp": str(jwt_data.get("iat")),
            }
        )
    except Exception as e:
        return jsonify({"message": "JWT验证失败", "error": str(e)}), 401


@api_bp.route("/users/<int:id>", methods=["PUT"])
@jwt_required()
def update_user(id):
    """更新用户信息"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只有管理员可以更新其他用户信�?
        if current_user.role != "admin" and current_user_id != id:
            return jsonify({"error": "权限不足"}), 403

        user = User.query.get_or_404(id)
        data = request.get_json()

        if "email" in data and data["email"] != user.email:
            # 检查新邮箱是否已被使用
            if User.query.filter_by(email=data["email"]).first():
                return jsonify({"error": "邮箱已被使用"}), 400
            user.email = data["email"]

        if "full_name" in data:
            user.full_name = data["full_name"]
        if "phone" in data:
            user.phone = data["phone"]

        # 只有管理员可以修改角色和激活状�?
        if current_user.role == "admin":
            if "role" in data:
                user.role = data["role"]
            if "is_active" in data:
                user.is_active = data["is_active"]

        # 如果提供了新密码
        if "password" in data and data["password"]:
            user.set_password(data["password"])

        db.session.commit()
        return jsonify({"message": "用户信息更新成功", "data": user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/users/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_user(id):
    """删除用户"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只有管理员可以删除用�?
        if current_user.role != "admin":
            return jsonify({"error": "权限不足"}), 403

        # 不能删除自己
        if current_user_id == id:
            return jsonify({"error": "不能删除自己的账�?"}), 400

        user = User.query.get_or_404(id)

        # 检查用户是否有未完成的调度任务
        from app.models.dispatch_task import DispatchTask

        pending_tasks = DispatchTask.query.filter(
            DispatchTask.assigned_to == id,
            DispatchTask.status.in_(["pending", "in_progress"]),
        ).count()

        if pending_tasks > 0:
            return (
                jsonify(
                    {"error": f"该用户有 {pending_tasks} 个未完成的调度任务，无法删除"}
                ),
                400,
            )

        # 检查是否有任何关联任务（作为创建者或执行者）
        # 如果有，则只能进行软删除（禁用账户）
        has_related_tasks = DispatchTask.query.filter(
            (DispatchTask.created_by == id) | (DispatchTask.assigned_to == id)
        ).first()

        if has_related_tasks:
            # 软删除：设为未激�?
            user.is_active = False
            db.session.commit()
            return jsonify(
                {
                    "message": "用户存在关联历史任务，已自动切换为禁用状�?",
                    "deleted_user": {
                        "id": user.id,
                        "username": user.username,
                        "is_active": False,
                    },
                }
            )

        # 记录用户信息用于日志（可选）
        user_info = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }

        db.session.delete(user)
        db.session.commit()

        # 双重检�?
        if User.query.get(id):
            return jsonify({"error": "删除操作未生效，请重�?"}), 500

        return jsonify({"message": "用户删除成功", "deleted_user": user_info})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route("/users/<int:id>", methods=["GET"])
@jwt_required()
def get_user_by_id(id):
    """根据ID获取单个用户信息"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只有管理员可以查看其他用户信息，或者用户查看自�?
        if current_user.role != "admin" and current_user_id != id:
            return jsonify({"error": "权限不足"}), 403

        user = User.query.get_or_404(id)
        return jsonify({"data": user.to_dict()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
