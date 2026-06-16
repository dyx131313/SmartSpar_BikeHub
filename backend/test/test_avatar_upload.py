#!/usr/bin/env python3
"""
测试头像上传功能
"""
import requests
import os
from datetime import datetime

import pytest


pytestmark = pytest.mark.skip(reason="manual external-server smoke test")

# 配置
API_BASE = "http://localhost:5000"
TEST_IMAGE_PATH = "test_avatar.jpg"

def create_test_image():
    """创建一个测试图片"""
    try:
        from PIL import Image, ImageDraw

        # 创建一个简单的测试图片
        img = Image.new('RGB', (200, 200), color = 'red')
        d = ImageDraw.Draw(img)
        d.text((10,10), "Test Avatar", fill=(255,255,0))

        # 保存图片
        img.save(TEST_IMAGE_PATH)
        print(f"创建测试图片: {TEST_IMAGE_PATH}")
        return True
    except ImportError:
        print("PIL 库未安装，使用简单的文本文件代替")
        # 创建一个文本文件作为测试
        with open(TEST_IMAGE_PATH, 'w') as f:
            f.write("This is a test image file")
        return True
    except Exception as e:
        print(f"创建测试图片失败: {e}")
        return False

def test_upload_without_token():
    """测试没有token的访问"""
    print("\n=== 测试没有token的访问 ===")

    # 创建测试图片
    if not create_test_image():
        return

    with open(TEST_IMAGE_PATH, 'rb') as f:
        files = {'avatar': f}
        response = requests.post(f"{API_BASE}/api/users/avatar", files=files)

    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")

    # 清理
    if os.path.exists(TEST_IMAGE_PATH):
        os.remove(TEST_IMAGE_PATH)

def test_upload_with_invalid_token():
    """测试无效token的访问"""
    print("\n=== 测试无效token的访问 ===")

    # 创建测试图片
    if not create_test_image():
        return

    headers = {
        'Authorization': 'Bearer invalid_token'
    }

    with open(TEST_IMAGE_PATH, 'rb') as f:
        files = {'avatar': f}
        response = requests.post(f"{API_BASE}/api/users/avatar", files=files, headers=headers)

    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")

    # 清理
    if os.path.exists(TEST_IMAGE_PATH):
        os.remove(TEST_IMAGE_PATH)

if __name__ == "__main__":
    print("开始测试头像上传功能...")

    # 首先测试没有认证的情况
    test_upload_without_token()

    # 然后测试无效token
    test_upload_with_invalid_token()

    print("\n测试完成！")
