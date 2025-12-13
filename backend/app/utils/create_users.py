# create_users.py
import sys
import os
from dotenv import load_dotenv 

backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(backend_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_CONFIG'] = 'development'

sys.path.insert(0, backend_root)

from app import create_app, db
from app.models.user import User

def create_users():
    app = create_app()
    with app.app_context():
        # 创建10个用户（ID 1-10）
        for user_id in range(1, 11):
            existing_user = User.query.get(user_id)
            if not existing_user:
                user = User(
                    id=user_id,
                    username=f'user_{user_id}',
                    email=f'user_{user_id}@example.com',
                    role='user',
                    full_name=f'用户{user_id}'
                )
                user.set_password('123456')
                db.session.add(user)
                print(f"已创建用户 ID: {user_id}")
        
        # 创建管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin_user = User(
                username='admin',
                email='admin@bikehub.com',
                role='admin',
                full_name='系统管理员'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            print("已创建管理员用户")
        
        db.session.commit()
        print("用户创建完成！")

if __name__ == "__main__":
    create_users()