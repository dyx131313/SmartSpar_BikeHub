from datetime import datetime
import os
import threading
from zoneinfo import ZoneInfo


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

        self.timezone_name = os.getenv("SYSTEM_TIMEZONE", "Asia/Shanghai")
        self.timezone = ZoneInfo(self.timezone_name)
        self.mode = os.getenv("SYSTEM_TIME_MODE", "real").strip().lower()
        self.base_virtual_time = self._read_base_virtual_time()
        self.start_real_time = datetime.now()
        self.time_scale = float(os.getenv("SYSTEM_TIME_SCALE", "1.0"))

        self._initialized = True

    def _read_base_virtual_time(self) -> datetime:
        raw_value = os.getenv("SYSTEM_BASE_TIME", "").strip()
        if raw_value:
            return datetime.fromisoformat(raw_value.replace("Z", "+00:00")).replace(tzinfo=None)
        return datetime.now(self.timezone).replace(tzinfo=None)

    def get_current_time(self) -> datetime:
        """Return current application time as a naive local datetime."""
        if self.mode == "real":
            return datetime.now(self.timezone).replace(tzinfo=None)

        now_real = datetime.now()
        elapsed_real = now_real - self.start_real_time
        elapsed_virtual = elapsed_real * self.time_scale
        return self.base_virtual_time + elapsed_virtual

    def get_current_time_str(self) -> str:
        return self.get_current_time().isoformat(timespec="seconds")


time_service = TimeService()
