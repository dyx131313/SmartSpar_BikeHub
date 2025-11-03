import os
from datetime import timedelta

class Config:
    """Flask应用配置类"""

    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'

    # 数据库配置
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'password'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or '3306'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'bikehub'

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True
    }

    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # 分页配置
    ITEMS_PER_PAGE = 20

    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads')

    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'app.log'

    # CORS配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

    # Redis配置（用于缓存和会话）
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # AI模型配置
    MODEL_PATH = os.environ.get('MODEL_PATH') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models')

    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建上传目录
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

        # 创建模型目录
        os.makedirs(Config.MODEL_PATH, exist_ok=True)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB}_dev?charset=utf8mb4'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

    # 生产环境使用更强的密钥
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置SECRET_KEY环境变量")

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("生产环境必须设置JWT_SECRET_KEY环境变量")


# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}