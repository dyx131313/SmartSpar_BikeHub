"""
认证工具函数
"""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
)
import logging

logger = logging.getLogger(__name__)

class JWTAuth:
    """JWT认证工具类"""

    @staticmethod
    def generate_token(user_data, expires_in=24*3600):
        """
        生成JWT token
        Args:
            user_data (dict): 用户数据
            expires_in (int): 过期时间（秒）
        Returns:
            str: JWT token
        """
        try:
            # 设置过期时间
            exp = datetime.utcnow() + timedelta(seconds=expires_in)

            # 构建payload
            payload = {
                'sub': str(user_data.get('user_id')),
                'user_id': user_data.get('user_id'),
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'role': user_data.get('role'),
                'exp': exp,
                'iat': datetime.utcnow(),
                'iss': 'bikehub',
                'aud': 'bikehub-users'
            }

            # 生成token
            token = jwt.encode(
                payload,
                current_app.config.get('JWT_SECRET_KEY', 'your-secret-key'),
                algorithm='HS256'
            )

            return token

        except Exception as e:
            logger.error(f"生成JWT token失败: {str(e)}")
            raise Exception(f"生成JWT token失败: {str(e)}")

    @staticmethod
    def verify_token(token):
        """
        验证JWT token
        Args:
            token (str): JWT token
        Returns:
            dict: 用户数据
        """
        try:
            # 优先尝试使用 aud/iss 验证（自定义生成的 token）
            payload = jwt.decode(
                token,
                current_app.config.get('JWT_SECRET_KEY', 'your-secret-key'),
                algorithms=['HS256'],
                audience='bikehub-users',
                issuer='bikehub'
            )

        except (jwt.InvalidAudienceError, jwt.InvalidIssuerError, jwt.MissingRequiredClaimError) as e:
            # 如果 token 来自 flask_jwt_extended，可能没有 aud/iss 声明，回退到仅签名校验
            try:
                payload = jwt.decode(
                    token,
                    current_app.config.get('JWT_SECRET_KEY', 'your-secret-key'),
                    algorithms=['HS256']
                )
            except jwt.ExpiredSignatureError:
                raise Exception('Token已过期')
            except jwt.InvalidTokenError as e2:
                raise Exception(f'无效的Token: {str(e2)}')
            except Exception as e2:
                logger.error(f"回退解码失败: {str(e2)}")
                raise Exception(f"验证JWT token失败: {str(e2)}")

        except jwt.ExpiredSignatureError:
            raise Exception('Token已过期')
        except jwt.InvalidTokenError as e:
            raise Exception(f'无效的Token: {str(e)}')
        except Exception as e:
            logger.error(f"验证JWT token失败: {str(e)}")
            raise Exception(f"验证JWT token失败: {str(e)}")

        # 检查是否过期（有些 token 的 exp 可能是 datetime 或 timestamp）
        try:
            exp = payload.get('exp')
            if exp:
                # 如果是 datetime 对象
                if isinstance(exp, datetime):
                    exp_dt = exp
                else:
                    try:
                        exp_dt = datetime.fromtimestamp(int(exp))
                    except Exception:
                        exp_dt = None

                if exp_dt and exp_dt < datetime.utcnow():
                    raise Exception('Token已过期')
        except Exception as e:
            logger.warning(f"检查 exp 失败或 token 已过期: {e}")

        return payload

    @staticmethod
    def refresh_token(refresh_token):
        """
        刷新JWT token
        Args:
            refresh_token (str): 刷新token
        Returns:
            str: 新的access token
        """
        try:
            # 验证刷新token
            payload = JWTAuth.verify_token(refresh_token)

            # 生成新的access token
            new_payload = {
                'sub': str(payload.get('sub')),
                'user_id': payload.get('user_id'),
                'username': payload.get('username'),
                'email': payload.get('email'),
                'role': payload.get('role')
            }

            return JWTAuth.generate_token(new_payload, expires_in=3600)  # 1小时

        except Exception as e:
            logger.error(f"刷新JWT token失败: {str(e)}")
            raise Exception(f"刷新JWT token失败: {str(e)}")

def token_required(f):
    """
    Token认证装饰器
    Args:
        f: 被装饰的函数
    Returns:
        function: 装饰后的函数
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # 从请求头获取token
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'error': '缺少认证token'}), 401

            # 解析token
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({'error': '无效的token格式'}), 401

            token = parts[1]

            # 验证token
            user_data = JWTAuth.verify_token(token)
            if not user_data:
                return jsonify({'error': '无效的token'}), 401

            # 将用户信息添加到请求上下文
            request.current_user = user_data
            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Token认证失败: {str(e)}")
            return jsonify({'error': str(e)}), 401

    return decorated

def admin_required(f):
    """
    管理员权限装饰器
    Args:
        f: 被装饰的函数
    Returns:
        function: 装饰后的函数
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # 验证token
            verify_jwt_in_request()

            # 获取用户信息
            user_data = get_jwt()
            user_role = user_data.get('role')

            # 如果token里没有role信息，兜底从数据库查询
            if not user_role:
                try:
                    from app.utils.database import get_db_connection
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT role FROM users WHERE id = %s", (get_jwt_identity(),))
                    db_user = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    if db_user:
                        user_role = db_user.get('role')
                except Exception as db_e:
                    logger.warning(f"查询用户角色失败: {db_e}")

            print(f"=== Admin Required Debug ===")
            print(f"User data: {user_data}")
            print(f"User role: {user_role}")
            print(f"Role type: {type(user_role)}")
            print(f"Role == 'admin': {user_role == 'admin'}")
            print("===========================")

            if user_role != 'admin':
                print(f"权限验证失败: 用户角色不是admin")
                return jsonify({'error': '需要管理员权限'}), 403

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"管理员权限验证失败: {str(e)}")
            return jsonify({'error': str(e)}), 401

    return decorated

def role_required(required_roles):
    """
    角色权限装饰器
    Args:
        required_roles (list): 需要的角色列表
    Returns:
        function: 装饰器函数
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                # 验证token
                verify_jwt_in_request()

                # 获取用户信息
                user_data = get_jwt()
                user_role = user_data.get('role')

                if user_role not in required_roles:
                    return jsonify({
                        'error': f'需要以下角色之一: {", ".join(required_roles)}'
                    }), 403

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"角色权限验证失败: {str(e)}")
                return jsonify({'error': str(e)}), 401

        return decorated
    return decorator

def get_current_user():
    """
    获取当前用户信息
    Returns:
        dict: 用户信息或None
    """
    try:
        # 尝试从请求上下文获取
        if hasattr(request, 'current_user'):
            return request.current_user

        # 从JWT token获取
        try:
            verify_jwt_in_request()
            user_data = get_jwt()
            return user_data
        except:
            return None

    except Exception as e:
        logger.error(f"获取当前用户失败: {str(e)}")
        return None

def is_admin():
    """
    检查当前用户是否为管理员
    Returns:
        bool: 是否为管理员
    """
    user_data = get_current_user()
    return user_data and user_data.get('role') == 'admin'

def has_role(role):
    """
    检查当前用户是否具有指定角色
    Args:
        role (str): 角色名称
    Returns:
        bool: 是否具有指定角色
    """
    user_data = get_current_user()
    return user_data and user_data.get('role') == role

def has_any_role(roles):
    """
    检查当前用户是否具有任一指定角色
    Args:
        roles (list): 角色列表
    Returns:
        bool: 是否具有任一指定角色
    """
    user_data = get_current_user()
    user_role = user_data.get('role') if user_data else None
    return user_role in roles

def extract_token_from_request():
    """
    从请求中提取token
    Returns:
        str or None: JWT token
    """
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None
    except Exception as e:
        logger.error(f"提取token失败: {str(e)}")
        return None

def verify_token_from_request():
    """
    验证请求中的token
    Returns:
        dict or None: 用户数据
    """
    token = extract_token_from_request()
    if token:
        try:
            return JWTAuth.verify_token(token)
        except Exception as e:
            logger.error(f"验证请求token失败: {str(e)}")
    return None

class AuthUtils:
    """认证工具类"""

    @staticmethod
    def hash_password(password):
        """
        哈希密码
        Args:
            password (str): 明文密码
        Returns:
            str: 哈希后的密码
        """
        import hashlib
        import secrets

        # 生成盐值
        salt = secrets.token_hex(16)

        # 哈希密码
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 迭代次数
        )

        return f"{salt}${password_hash.hex()}"

    @staticmethod
    def verify_password(password, hashed_password):
        """
        验证密码
        Args:
            password (str): 明文密码
            hashed_password (str): 哈希密码
        Returns:
            bool: 密码是否正确
        """
        import hashlib

        try:
            # 分离盐值和哈希值
            salt, hash_hex = hashed_password.split('$')

            # 计算哈希值
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )

            # 比较
            return password_hash.hex() == hash_hex

        except Exception as e:
            logger.error(f"密码验证失败: {str(e)}")
            return False

    @staticmethod
    def generate_reset_token(email, expires_in=3600):
        """
        生成重置密码token
        Args:
            email (str): 用户邮箱
            expires_in (int): 过期时间（秒）
        Returns:
            str: 重置token
        """
        payload = {
            'email': email,
            'type': 'password_reset',
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }

        return jwt.encode(
            payload,
            current_app.config.get('JWT_SECRET_KEY', 'your-secret-key'),
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(token):
        """
        验证重置密码token
        Args:
            token (str): 重置token
        Returns:
            dict: token数据或None
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config.get('JWT_SECRET_KEY', 'your-secret-key'),
                algorithms=['HS256']
            )

            if payload.get('type') != 'password_reset':
                return None

            return payload

        except Exception as e:
            logger.error(f"验证重置token失败: {str(e)}")
            return None