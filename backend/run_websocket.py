#!/usr/bin/env python3
"""
WebSocket服务器启动脚本
"""
import sys
import os
import asyncio
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes.websocket import websocket_server

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/websocket.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """主函数"""
    try:
        logger.info("正在启动WebSocket服务器...")

        # 运行WebSocket服务器
        websocket_server.run()

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭WebSocket服务器...")
    except Exception as e:
        logger.error(f"启动WebSocket服务器失败: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("WebSocket服务器已停止")

if __name__ == "__main__":
    main()