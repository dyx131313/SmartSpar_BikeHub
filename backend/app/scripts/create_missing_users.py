"""创建缺失用户的安全脚本：只插入不存在的用户（ID 1-10），避免重复。
用法: python3 backend/app/scripts/create_missing_users.py
"""
import sys
import os

# 确保脚本在项目任意位置执行时可以导入 `app` 包
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app import db

app = create_app()

with app.app_context():
    from app.models.user import User

    created = []
    for uid in range(1, 11):
        existing = User.query.get(uid)
        if existing:
            continue

        # 生成一个不会冲突的用户名
        base_username = f"testuser{uid}"
        username = base_username
        i = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{i}"
            i += 1

        user = User(
            id=uid,
            username=username,
            email=f"{username}@example.com",
            role="operator",
            full_name=f"测试用户{uid}",
        )
        user.set_password("test123")
        db.session.add(user)
        created.append(uid)

    if created:
        try:
            db.session.commit()
            print(f"已创建用户 ID: {created}，默认密码: test123")
        except Exception as e:
            db.session.rollback()
            print(f"提交失败: {e}")
    else:
        print("没有需要创建的用户（ID 1-10 已存在）。")
