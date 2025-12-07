import os
from dotenv import load_dotenv
load_dotenv()  # ✅ 关键：加载 .env 文件

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
from app.config.config import config
#from app.models import *

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
    cors.init_app(app, origins=app.config['CORS_ORIGINS'],
                  supports_credentials=True,
                  allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
                  methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    jwt.init_app(app)

    # 配置JWT错误处理
    configure_jwt_errors(app)

    # **延后导入 models，避免循环导入**
    # 这里采用相对导入，确保模型类被注册到 SQLAlchemy 中
    with app.app_context():
        from . import models   # 或者 from app import models
    
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
    from app.routes.static import static_bp
    app.register_blueprint(static_bp)

def configure_jwt_errors(app):
    """配置JWT错误处理"""
    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Token过期回调"""
        return {'msg': 'Token已过期，请重新登录'}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """无效Token回调"""
        return {'msg': '无效的Token，请重新登录'}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """缺少Token回调"""
        return {'msg': '需要提供Token才能访问此接口'}, 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        """Token需要刷新回调"""
        return {'msg': '需要新鲜的Token，请重新登录'}, 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Token被撤销回调"""
        return {'msg': 'Token已被撤销，请重新登录'}, 401


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

    @app.cli.command()
    def create_dispatcher():
        """创建调度员用户"""
        from app.models.user import User
        dispatcher = User(
            username='dispatcher',
            email='dispatcher@bikehub.com',
            role='dispatcher',
            full_name='调度员'
        )
        dispatcher.set_password('dispatcher123')
        db.session.add(dispatcher)
        db.session.commit()
        print('调度员用户创建成功 - 用户名: dispatcher, 密码: dispatcher123')

    @app.cli.command()
    def create_operator():
        """创建运维员用户"""
        from app.models.user import User
        operator = User(
            username='operator',
            email='operator@bikehub.com',
            role='operator',
            full_name='运维员'
        )
        operator.set_password('operator123')
        db.session.commit()
        print('运维员用户创建成功 - 用户名: operator, 密码: operator123')

    @app.cli.command()
    def create_test_users():
        """创建测试用户"""
        from app.models.user import User

        # 创建管理员
        admin = User(
            username='admin',
            email='admin@bikehub.com',
            role='admin',
            full_name='系统管理员'
        )
        admin.set_password('admin123')
        db.session.add(admin)

        # 创建调度员
        dispatcher = User(
            username='dispatcher',
            email='dispatcher@bikehub.com',
            role='dispatcher',
            full_name='调度员'
        )
        dispatcher.set_password('dispatcher123')
        db.session.add(dispatcher)

        # 创建运维员
        operator = User(
            username='operator',
            email='operator@bikehub.com',
            role='operator',
            full_name='运维员'
        )
        operator.set_password('operator123')
        db.session.add(operator)

        db.session.commit()
        print('测试用户创建成功:')
        print('管理员 - 用户名: admin, 密码: admin123')
        print('调度员 - 用户名: dispatcher, 密码: dispatcher123')
        print('运维员 - 用户名: operator, 密码: operator123')

    @app.cli.command()
    def train_demand_model():
        """训练需求预测模型"""
        from app.services.demand_predictor import get_demand_predictor

        print("开始训练需求预测模型...")
        try:
            predictor = get_demand_predictor()
            train_data_path = 'train.csv'

            if not os.path.exists(train_data_path):
                print(f"错误: 训练数据文件 {train_data_path} 不存在")
                return

            results = predictor.train(train_data_path)

            print("\n=== 模型训练完成 ===")
            print(f"最佳模型: {results['best_model']}")
            print("训练结果:")
            for model_name, metrics in results['training_results'].items():
                print(f"  {model_name}: MAE={metrics['mae']:.2f}, R2={metrics['r2']:.3f}")

            print(f"\n模型已保存到: {predictor.model_path}")
            print("特征重要性:")

            importance = predictor.get_feature_importance()
            sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            for feature, score in sorted_importance[:10]:
                print(f"  {feature}: {score:.4f}")

        except Exception as e:
            print(f"训练失败: {e}")

    @app.cli.command()
    def test_demand_prediction():
        """测试需求预测功能"""
        from app.services.demand_predictor import predict_demand_for_station

        print("测试需求预测功能...")

        test_cases = [
            {
                'name': '早高峰工作日',
                'params': {
                    'station_type': 1,
                    'temp': 22.0,
                    'is_holiday': 0,
                    'weather': 0,
                    'weekday': 1,
                    'date_str': '2024/9/2 8:00'
                }
            },
            {
                'name': '周末午后',
                'params': {
                    'station_type': 2,
                    'temp': 28.0,
                    'is_holiday': 0,
                    'weather': 0,
                    'weekday': 6,
                    'date_str': '2024/9/7 14:00'
                }
            }
        ]

        try:
            for test_case in test_cases:
                result = predict_demand_for_station(**test_case['params'])
                print(f"\n{test_case['name']}:")
                print(f"  预测需求量: {result['prediction']}")
                print(f"  置信度: {result['confidence']:.3f}")
                print(f"  模型类型: {result['model_type']}")

        except Exception as e:
            print(f"测试失败: {e}")