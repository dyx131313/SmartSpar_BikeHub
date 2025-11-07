import os

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()
# 调试：打印所有环境变量
print("=== 环境变量验证 ===")
print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
print(f"JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY')}")
print(f"SECRET_KEY 长度: {len(os.getenv('SECRET_KEY', ''))}")
print("===================")
from app import create_app, db
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)