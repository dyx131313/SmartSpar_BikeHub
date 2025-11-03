import json
import csv
from datetime import datetime
from app import db
from app.models.demand_data import DemandData
from app.models.station import Station
from app.models.user import User

class DataImporter:
    """数据导入工具类"""

    @staticmethod
    def import_demand_data_from_json(json_file_path):
        """从JSON文件导入需求数据"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            imported_count = 0
            skipped_count = 0
            errors = []

            for item in data:
                try:
                    demand_item = DemandData.create_from_json(item)

                    # 如果提供了station_id，验证站点是否存在
                    if 'station_id' in item and item['station_id']:
                        station = Station.query.get(item['station_id'])
                        if station:
                            demand_item.station_id = item['station_id']
                        else:
                            # 尝试根据站点类型找到第一个匹配的站点
                            station = Station.query.filter_by(station_type=item['station_type']).first()
                            if station:
                                demand_item.station_id = station.id

                    db.session.add(demand_item)
                    imported_count += 1
                except Exception as e:
                    skipped_count += 1
                    errors.append(f"数据项 {item.get('timestamp', 'unknown')} 导入失败: {str(e)}")

            db.session.commit()
            return {
                'success': True,
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'errors': errors
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def import_demand_data_from_csv(csv_file_path):
        """从CSV文件导入需求数据"""
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                imported_count = 0
                skipped_count = 0
                errors = []

                for row in reader:
                    try:
                        # 转换数据格式
                        item = {
                            'timestamp': row['timestamp'],
                            'station_type': row['station_type'],
                            'weekday': int(row['weekday']),
                            'is_holiday': int(row.get('is_holiday', 0)),
                            'weather': row['weather'],
                            'temp': float(row['temp']),
                            'demand': int(row['demand'])
                        }

                        demand_item = DemandData.create_from_json(item)

                        # 如果提供了station_id，验证站点是否存在
                        if 'station_id' in row and row['station_id']:
                            station = Station.query.get(int(row['station_id']))
                            if station:
                                demand_item.station_id = station['station_id']

                        db.session.add(demand_item)
                        imported_count += 1
                    except Exception as e:
                        skipped_count += 1
                        errors.append(f"行 {reader.line_num} 导入失败: {str(e)}")

                db.session.commit()
                return {
                    'success': True,
                    'imported_count': imported_count,
                    'skipped_count': skipped_count,
                    'errors': errors
                }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_sample_data():
        """创建示例数据"""
        try:
            # 确保至少有一个站点
            station = Station.query.first()
            if not station:
                station = Station(
                    name='示例站点',
                    station_type='canteen',
                    latitude=31.2304,
                    longitude=121.4737,
                    capacity=20,
                    description='示例站点用于测试'
                )
                db.session.add(station)
                db.session.commit()

            # 创建示例需求数据
            sample_data = [
                {
                    "timestamp": "2025-07-01 08:00:00",
                    "station_type": "canteen",
                    "weekday": 2,
                    "is_holiday": 0,
                    "weather": "rain",
                    "temp": 28.4,
                    "demand": 14,
                    "station_id": station.id
                },
                {
                    "timestamp": "2025-07-01 08:15:00",
                    "station_type": "canteen",
                    "weekday": 2,
                    "is_holiday": 0,
                    "weather": "rain",
                    "temp": 28.6,
                    "demand": 17,
                    "station_id": station.id
                },
                {
                    "timestamp": "2025-07-01 08:30:00",
                    "station_type": "canteen",
                    "weekday": 2,
                    "is_holiday": 0,
                    "weather": "cloudy",
                    "temp": 28.8,
                    "demand": 19,
                    "station_id": station.id
                },
                {
                    "timestamp": "2025-07-01 12:00:00",
                    "station_type": "canteen",
                    "weekday": 2,
                    "is_holiday": 0,
                    "weather": "sunny",
                    "temp": 31.5,
                    "demand": 25,
                    "station_id": station.id
                },
                {
                    "timestamp": "2025-07-01 18:00:00",
                    "station_type": "dormitory",
                    "weekday": 2,
                    "is_holiday": 0,
                    "weather": "cloudy",
                    "temp": 30.2,
                    "demand": 22,
                    "station_id": station.id
                }
            ]

            for item in sample_data:
                demand_item = DemandData.create_from_json(item)
                db.session.add(demand_item)

            db.session.commit()
            return {
                'success': True,
                'message': f'成功创建 {len(sample_data)} 条示例需求数据'
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_admin_user():
        """创建管理员用户"""
        try:
            # 检查是否已存在管理员用户
            admin = User.query.filter_by(username='admin').first()
            if admin:
                return {
                    'success': True,
                    'message': '管理员用户已存在'
                }

            admin = User(
                username='admin',
                email='admin@bikehub.com',
                role='admin',
                full_name='系统管理员'
            )
            admin.set_password('admin123')

            db.session.add(admin)
            db.session.commit()

            return {
                'success': True,
                'message': '管理员用户创建成功 - 用户名: admin, 密码: admin123'
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }