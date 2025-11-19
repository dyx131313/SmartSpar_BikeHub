from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from datetime import datetime
from app import db
from app.models.user import User
from app.routes import api_bp


@api_bp.route("/auth/register", methods=["POST"])
def register():
    """用户注册"""
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ["username", "email", "password"]
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({"error": f"{field} 不能为空"}), 400

        # 验证用户名格式
        username = data["username"].strip()
        if len(username) < 3 or len(username) > 20:
            return jsonify({"error": "用户名长度必须在3-20个字符之间"}), 400
        if not username.replace("_", "").replace("-", "").isalnum():
            return jsonify({"error": "用户名只能包含字母、数字、下划线和连字符"}), 400

        # 验证密码强度
        password = data["password"]
        if len(password) < 6:
            return jsonify({"error": "密码长度至少6个字符"}), 400

        # 验证邮箱格式
        email = data["email"].strip().lower()
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return jsonify({"error": "邮箱格式不正确"}), 400

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "用户名已存在"}), 400

        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "邮箱已被注册"}), 400

        # 创建新用户，默认角色为 'user'
        user = User(
            username=username,
            email=email,
            role="user",  # 注册用户默认为普通用户
            full_name=data.get("full_name", "").strip(),
            phone=data.get("phone", "").strip(),
            is_active=True,
            email_verified=False,  # 需要邮箱验证
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # 创建访问令牌
        access_token = create_access_token(identity=str(user.id))

        return (
            jsonify(
                {
                    "message": "注册成功",
                    "access_token": access_token,
                    "user": user.to_dict(),
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"注册失败: {str(e)}"}), 500


@api_bp.route("/auth/login", methods=["POST"])
def login():
    """用户登录"""
    try:
        data = request.get_json()

        if not data or not data.get("username") or not data.get("password"):
            return jsonify({"error": "用户名和密码不能为空"}), 400

        user = User.query.filter_by(username=data["username"]).first()

        if user and user.check_password(data["password"]) and user.is_active:
            access_token = create_access_token(identity=str(user.id))
            return jsonify({"access_token": access_token, "user": user.to_dict()})
        else:
            return jsonify({"error": "用户名或密码错误"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    """用户登出"""
    try:
        current_user_id = get_jwt_identity()
        jti = get_jwt()["jti"]  # 获取JWT ID

        # 在实际应用中，你可以将jti添加到黑名单中
        # 这里简化处理，只返回成功消息
        # 客户端应该删除本地存储的token

        # 更新用户最后登录时间（可选）
        user = User.query.get(current_user_id)
        if user:
            # 可以在这里记录登出时间等日志信息
            pass

        return jsonify(
            {"message": "登出成功", "logout_time": datetime.now().isoformat()}
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
            return jsonify({"error": "用户不存在"}), 404

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

        # 只有管理员可以查看所有用户
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

        # 只有管理员可以创建用户
        if current_user.role != "admin":
            return jsonify({"error": "权限不足"}), 403

        data = request.get_json()

        # 检查用户名是否已存在
        if User.query.filter_by(username=data["username"]).first():
            return jsonify({"error": "用户名已存在"}), 400

        # 检查邮箱是否已存在
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "邮箱已存在"}), 400

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
            return jsonify({"error": "用户不存在"}), 404

        return jsonify({"data": user.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/auth/debug-headers", methods=["GET", "POST"])
def debug_headers():
    """调试请求头 - 不验证JWT"""
    from flask import request

    auth_header = request.headers.get("Authorization", "")
    headers_dict = dict(request.headers)

    return jsonify(
        {
            "message": "请求头调试信息",
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

        # 只有管理员可以更新其他用户信息
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

        # 只有管理员可以修改角色和激活状态
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

        # 只有管理员可以删除用户
        if current_user.role != "admin":
            return jsonify({"error": "权限不足"}), 403

        # 不能删除自己
        if current_user_id == id:
            return jsonify({"error": "不能删除自己的账户"}), 400

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
            # 软删除：设为未激活
            user.is_active = False
            db.session.commit()
            return jsonify(
                {
                    "message": "用户存在关联历史任务，已自动切换为禁用状态",
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

        # 双重检查
        if User.query.get(id):
            return jsonify({"error": "删除操作未生效，请重试"}), 500

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

        # 只有管理员可以查看其他用户信息，或者用户查看自己
        if current_user.role != "admin" and current_user_id != id:
            return jsonify({"error": "权限不足"}), 403

        user = User.query.get_or_404(id)
        return jsonify({"data": user.to_dict()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
