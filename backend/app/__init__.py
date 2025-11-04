from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
import os
from app.config.config import config
from app.models import *

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()

def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    jwt.init_app(app)

    # 配置日志
    configure_logging(app)

    # 注册蓝图
    register_blueprints(app)

    # 注册错误处理器
    register_error_handlers(app)

    # 注册CLI命令
    register_cli_commands(app)

    return app

def configure_logging(app):
    """配置日志"""
    if not app.debug and not app.testing:
        # 配置文件日志
        log_file = app.config.get('LOG_FILE')
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
            app.logger.addHandler(file_handler)

        app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        app.logger.info('SmartSpar BikeHub Backend startup')

def register_blueprints(app):
    """注册蓝图"""
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

def register_error_handlers(app):
    """注册错误处理器"""
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(400)
    def bad_request_error(error):
        return {'error': 'Bad request'}, 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return {'error': 'Unauthorized'}, 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Forbidden'}, 403

def register_cli_commands(app):
    """注册CLI命令"""
    @app.cli.command()
    def init_db():
        """初始化数据库"""
        db.create_all()
        print('数据库初始化完成')

    @app.cli.command()
    def reset_db():
        """重置数据库"""
        db.drop_all()
        db.create_all()
        print('数据库重置完成')

    @app.cli.command()
    def create_admin():
        """创建管理员用户"""
        from app.models.user import User
        admin = User(
            username='admin',
            email='admin@bikehub.com',
            role='admin',
            full_name='系统管理员'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('管理员用户创建成功 - 用户名: admin, 密码: admin123')