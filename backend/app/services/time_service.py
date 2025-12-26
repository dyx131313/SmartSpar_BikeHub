from datetime import datetime, timedelta
import threading


class TimeService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TimeService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 初始虚拟时间：2025-12-08 00:00:00
        self.base_virtual_time = datetime(2025, 12, 8, 0, 0, 0)
        # 记录服务启动时的真实时间
        self.start_real_time = datetime.now()
        # 时间流逝倍率 (1.0 = 真实时间流逝, 60.0 = 1分钟顶1小时)
        # 用户要求"按真实时间流逝"，所以设为 1.0
        self.time_scale = 1.0

        self._initialized = True

    def get_current_time(self) -> datetime:
        """获取当前虚拟时间"""
        now_real = datetime.now()
        elapsed_real = now_real - self.start_real_time
        elapsed_virtual = elapsed_real * self.time_scale
        return self.base_virtual_time + elapsed_virtual

    def get_current_time_str(self) -> str:
        """获取ISO格式的当前虚拟时间字符串"""
        return self.get_current_time().isoformat(timespec="seconds")


# 全局单例
time_service = TimeService()
