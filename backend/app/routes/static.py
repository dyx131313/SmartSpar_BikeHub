import os
from flask import Blueprint, send_from_directory, current_app, abort

static_bp = Blueprint('static', __name__)

@static_bp.route('/uploads/avatars/<path:filename>')
def serve_avatar(filename):
    """服务头像文件"""
    try:
        avatar_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        file_path = os.path.join(avatar_dir, filename)

        # 添加调试日志
        current_app.logger.info(f"Attempting to serve avatar: {file_path}")
        current_app.logger.info(f"File exists: {os.path.exists(file_path)}")
        current_app.logger.info(f"File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'}")

        # 添加CORS头
        response = send_from_directory(avatar_dir, filename)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    except FileNotFoundError:
        current_app.logger.error(f"Avatar file not found: {filename}")
        abort(404)
    except Exception as e:
        current_app.logger.error(f"Error serving avatar {filename}: {str(e)}")
        abort(500)

@static_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    """服务上传的文件"""
    try:
        response = send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    except FileNotFoundError:
        abort(404)