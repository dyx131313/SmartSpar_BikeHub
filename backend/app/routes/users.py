from flask import request, jsonify, current_app
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
from app.models.user import User, UserLog
from app.routes import api_bp
from werkzeug.utils import secure_filename
import os
import uuid
import mimetypes
from app.models.user import User
from app.models.verification_code import VerificationCode
from app.routes import api_bp
from app.utils.email_utils import send_verification_email


@api_bp.route("/auth/register", methods=["POST"])
def register():
    """User registration"""
    try:
        data = request.get_json(silent=True)

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

        # Validate password presence (require non-empty)
        password = data["password"]
        if not password or len(str(password).strip()) == 0:
            return jsonify({"error": "Password is required"}), 400

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

        # Create access token with user role
        additional_claims = {
            'role': user.role,
            'username': user.username,
            'email': user.email
        }
        access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

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
        data = request.get_json(silent=True) or {}

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
            # 创建包含用户角色信息的 JWT token
            additional_claims = {
                'role': user.role,
                'username': user.username,
                'email': user.email
            }
            access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
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
        current_user_id = int(get_jwt_identity())
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


@api_bp.route("/auth/debug", methods=["GET"])
def debug_auth():
    """调试端点：检查当前用户的身份信息"""
    try:
        from flask_jwt_extended import get_jwt, get_jwt_identity

        current_user_id = int(get_jwt_identity())
        jwt_data = get_jwt()

        print(f"Current user ID: {current_user_id}")
        print(f"JWT data: {jwt_data}")

        return {
            "user_id": current_user_id,
            "jwt_claims": jwt_data,
            "message": "Debug info sent"
        }
    except Exception as e:
        return {"error": str(e)}, 500


@api_bp.route("/auth/email/verify-bind", methods=["POST"])
@jwt_required()
def verify_bind_email():
    """Verify email binding code and update user's email"""
    try:
        current_user_id = int(get_jwt_identity())
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
            expires_in_minutes=10,
        )
        db.session.add(verification)
        db.session.commit()

        subject = "BikeHub - Password reset verification code"
        body = (
            f" 你的“重置密码”验证码是：{code}\n\n"
            f" 该验证码将在1分钟后过期，请尽快使用。如果您未请求重置密码，请忽略此邮件。"
        )

        body = (
            f"Your password reset verification code is: {code}\n\n"
            "This code will expire in 10 minutes. "
            "If you did not request a password reset, please ignore this email."
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
        data = request.get_json(silent=True) or {}
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
        current_user_id = int(get_jwt_identity())
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
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return jsonify({"error": "用户不存在或已被禁用"}), 401

        # 创建新的访问令牌
        additional_claims = {
            'role': user.role,
            'username': user.username,
            'email': user.email
        }
        new_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

        return jsonify({"access_token": new_token, "user": user.to_dict()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """获取当前登录用户信息"""
    try:
        current_user_id = int(get_jwt_identity())
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
        current_user_id = int(get_jwt_identity())
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
        current_user_id = int(get_jwt_identity())
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
        current_user_id = int(get_jwt_identity())
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
        current_user_id = int(get_jwt_identity())
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
        current_user_id = int(get_jwt_identity())
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
        current_user_id = int(get_jwt_identity())
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
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)

        # 只有管理员可以查看其他用户信息，或者用户查看自�?
        if current_user.role != "admin" and current_user_id != id:
            return jsonify({"error": "权限不足"}), 403

        user = User.query.get_or_404(id)
        return jsonify({"data": user.to_dict()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def allowed_avatar_file(filename):
    """验证头像文件类型"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    allowed_mimetypes = {'image/jpeg', 'image/jpg', 'image/png', 'image/gif'}

    # 检查文件扩展名
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_extensions:
            return False

    # 检查MIME类型
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type and mime_type not in allowed_mimetypes:
        return False

    return True


@api_bp.route("/users/avatar", methods=["POST"])
@jwt_required()
def upload_avatar():
    try:
        if 'avatar' not in request.files:
            return jsonify({"error": "没有文件部分"}), 400
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({"error": "未选择文件"}), 400

        # 验证文件大小（限制为2MB）
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > 2 * 1024 * 1024:  # 2MB
            return jsonify({"error": "文件大小不能超过2MB"}), 400

        # 1. 确保目录存在
        # 物理存储路径：backend/app/static/uploads/avatars
        avatar_dir = os.path.abspath(os.path.join(current_app.static_folder, 'uploads', 'avatars'))
        if not os.path.exists(avatar_dir):
            os.makedirs(avatar_dir, mode=0o755, exist_ok=True)

        # 2. 生成文件名
        current_user_id = int(get_jwt_identity())
        ext = os.path.splitext(file.filename)[1]
        new_filename = f"{current_user_id}_{uuid.uuid4().hex}{ext}"
        
        # 3. 保存文件
        file_path = os.path.join(avatar_dir, new_filename)
        file.save(file_path)

        # 4. 生成返回给前端的 URL (必须以 /static 开头)
        avatar_url = f"/static/uploads/avatars/{new_filename}"

        # 5. 更新数据库
        user = User.query.get(current_user_id)
        # 如果旧头像存在，建议在这里执行 os.remove(旧路径) 逻辑
        user.avatar_url = avatar_url
        db.session.commit()

        return jsonify({
            "message": "上传成功",
            "data": {"avatar_url": avatar_url, "file_path": file_path}
        })

    except Exception as e:
        # 这里会捕获所有错误并返回 JSON，防止前端解析失败
        db.session.rollback()
        print(f"DEBUG ERROR: {str(e)}") # 在服务器后台查看具体报错
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


@api_bp.route("/users/avatar", methods=["DELETE"])
@jwt_required()
def delete_avatar():
    """删除用户头像"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "用户不存在"}), 404

        if not user.avatar_url:
            return jsonify({"message": "用户没有头像"}), 200

        # 删除头像文件
        avatar_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        filename = os.path.basename(user.avatar_url)
        file_path = os.path.join(avatar_dir, filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        # 清除用户头像URL
        user.avatar_url = None
        user.updated_at = datetime.utcnow()
        db.session.commit()

        # 记录操作日志
        log_entry = UserLog(
            user_id=user.id,
            action='delete_avatar',
            resource_type='user',
            resource_id=user.id,
            description=f'用户删除头像: {filename}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            status='success'
        )
        db.session.add(log_entry)
        db.session.commit()

        return jsonify({"message": "头像删除成功"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
