"""为缺少 <= system_time 的 BikeHistory 的站点回填一条初始记录。
用法: python3 backend/app/scripts/backfill_bike_history.py
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app, db

app = create_app()

with app.app_context():
    from app.models.station import Station
    from app.models.bike_history import BikeHistory
    from app.services.time_service import time_service
    from sqlalchemy import desc

    system_time = time_service.get_current_time()

    created = []
    for station in Station.query.all():
        # 查找 timestamp <= system_time 的最新一条记录
        latest = (
            BikeHistory.query
            .filter(BikeHistory.station_id == station.id, BikeHistory.timestamp <= system_time)
            .order_by(BikeHistory.timestamp.desc())
            .first()
        )

        if latest:
            continue

        # 没有符合条件的记录，插入一条
        bh = BikeHistory(
            station_id=station.id,
            timestamp=system_time,
            available_bikes=station.capacity,
            available_docks=0,
            total_bikes=station.capacity,
            total_docks=station.capacity,
            is_station_active=True,
            last_report_time=system_time,
        )
        db.session.add(bh)
        created.append(station.id)

    if created:
        try:
            db.session.commit()
            print(f"为站点创建了初始 BikeHistory：{created}")
        except Exception as e:
            db.session.rollback()
            print(f"提交失败: {e}")
    else:
        print("没有需要回填的站点（所有站点已有 <= system_time 的 BikeHistory）。")
