import json
import csv
from datetime import datetime
from app import db
from app.models.demand_data import DemandData
from app.models.station import Station
from app.models.user import User

class DataImporter:
    """数据导入工具类（支持ISO 8601格式）"""

    @staticmethod
    def parse_datetime(timestamp_str):
        """解析时间字符串，支持多种格式"""
        formats = [
            '%Y-%m-%dT%H:%M:%S',       # ISO格式: 2024-01-15T06:00:00
            '%Y-%m-%dT%H:%M:%S.%f',    # 带微秒的ISO格式
            '%Y-%m-%d %H:%M:%S',       # 空格分隔格式
            '%Y-%m-%d'                 # 只有日期
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"无法解析时间格式: {timestamp_str}")

    @staticmethod
    def convert_to_iso_format(item):
        """将数据项转换为ISO格式"""
        if 'timestamp' in item and item['timestamp']:
            try:
                # 如果不是ISO格式，转换为ISO格式
                dt = DataImporter.parse_datetime(item['timestamp'])
                item['timestamp'] = dt.isoformat()
            except ValueError as e:
                raise ValueError(f"时间格式错误: {item['timestamp']} - {str(e)}")
        
        # 确保字段类型正确
        if 'weekday' in item:
            item['weekday'] = int(item['weekday'])
        
        if 'is_holiday' in item:
            # 支持布尔值和整数
            if isinstance(item['is_holiday'], bool):
                item['is_holiday'] = 1 if item['is_holiday'] else 0
            else:
                item['is_holiday'] = int(item['is_holiday'])
        
        if 'temp' in item:
            item['temp'] = float(item['temp'])
        
        if 'demand' in item:
            item['demand'] = int(item['demand'])
        
        if 'station_id' in item and item['station_id']:
            item['station_id'] = int(item['station_id'])
        
        return item

    @staticmethod
    def import_demand_data_from_json(json_file_path):
        """从JSON文件导入需求数据（支持ISO 8601格式）"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            imported_count = 0
            skipped_count = 0
            errors = []

            for idx, item in enumerate(data):
                try:
                    # 转换数据格式为ISO
                    item = DataImporter.convert_to_iso_format(item)
                    
                    # 创建需求数据对象
                    demand_item = DemandData.create_from_json(item)

                    # 验证和处理station_id
                    if 'station_id' in item and item['station_id']:
                        station = Station.query.get(item['station_id'])
                        if station:
                            demand_item.station_id = item['station_id']
                        else:
                            # 尝试根据站点类型找到第一个匹配的站点
                            station = Station.query.filter_by(station_type=item['station_type']).first()
                            if station:
                                demand_item.station_id = station.id
                            else:
                                errors.append(f"数据项 {idx+1}: 站点ID {item['station_id']} 不存在，且无匹配站点类型")
                                skipped_count += 1
                                continue
                    else:
                        # 如果没有提供station_id，尝试根据站点类型关联
                        station = Station.query.filter_by(station_type=item['station_type']).first()
                        if station:
                            demand_item.station_id = station.id

                    db.session.add(demand_item)
                    imported_count += 1
                    
                    # 每100条提交一次，提高性能
                    if imported_count % 100 == 0:
                        db.session.commit()
                        
                except Exception as e:
                    skipped_count += 1
                    errors.append(f"数据项 {idx+1} ({item.get('timestamp', 'unknown')}) 导入失败: {str(e)}")

            db.session.commit()
            
            return {
                'success': True,
                'message': f'数据导入完成，成功 {imported_count} 条，失败 {skipped_count} 条',
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'errors': errors[:10] if errors else []
            }

        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'JSON文件格式错误: {str(e)}'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def import_demand_data_from_csv(csv_file_path):
        """从CSV文件导入需求数据（支持ISO 8601格式）"""
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                imported_count = 0
                skipped_count = 0
                errors = []

                for row_idx, row in enumerate(reader, start=1):
                    try:
                        # 转换数据格式
                        item = {
                            'timestamp': row.get('timestamp', ''),
                            'station_type': row.get('station_type', 'unknown'),
                            'weekday': int(row.get('weekday', 1)),
                            'is_holiday': int(row.get('is_holiday', 0)),
                            'weather': row.get('weather', 'unknown'),
                            'temp': float(row.get('temp', 20.0)),
                            'demand': int(row.get('demand', 0))
                        }
                        
                        # 如果CSV中有station_id列
                        if 'station_id' in row and row['station_id']:
                            item['station_id'] = row['station_id']
                        
                        # 转换为ISO格式
                        item = DataImporter.convert_to_iso_format(item)
                        
                        # 创建需求数据对象
                        demand_item = DemandData.create_from_json(item)

                        # 处理station_id
                        if 'station_id' in item and item['station_id']:
                            station = Station.query.get(item['station_id'])
                            if station:
                                demand_item.station_id = item['station_id']
                            else:
                                station = Station.query.filter_by(station_type=item['station_type']).first()
                                if station:
                                    demand_item.station_id = station.id

                        db.session.add(demand_item)
                        imported_count += 1
                        
                        # 每100条提交一次
                        if imported_count % 100 == 0:
                            db.session.commit()
                            
                    except Exception as e:
                        skipped_count += 1
                        errors.append(f"第 {row_idx} 行导入失败: {str(e)}")

                db.session.commit()
                return {
                    'success': True,
                    'message': f'CSV导入完成，成功 {imported_count} 行，失败 {skipped_count} 行',
                    'imported_count': imported_count,
                    'skipped_count': skipped_count,
                    'errors': errors[:10] if errors else []
                }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def import_stations_from_json(json_file_path):
        """从JSON文件导入站点数据"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            imported_count = 0
            updated_count = 0
            errors = []

            for idx, item in enumerate(data):
                try:
                    # 检查是否已存在相同ID的站点
                    existing_station = Station.query.get(item.get('id'))
                    
                    if existing_station:
                        # 更新现有站点
                        existing_station.name = item.get('name', existing_station.name)
                        existing_station.station_type = item.get('station_type', existing_station.station_type)
                        existing_station.latitude = float(item.get('latitude', existing_station.latitude))
                        existing_station.longitude = float(item.get('longitude', existing_station.longitude))
                        existing_station.capacity = int(item.get('capacity', existing_station.capacity))
                        existing_station.description = item.get('description', existing_station.description)
                        updated_count += 1
                    else:
                        # 创建新站点
                        station = Station(
                            name=item.get('name', f'站点{idx+1}'),
                            station_type=item.get('station_type', 'unknown'),
                            latitude=float(item.get('latitude', 0.0)),
                            longitude=float(item.get('longitude', 0.0)),
                            capacity=int(item.get('capacity', 20)),
                            description=item.get('description', '')
                        )
                        db.session.add(station)
                        imported_count += 1
                        # 初始化站点的单车历史，使当前可用车辆等于站点容量
                        try:
                            from app.models.bike_history import BikeHistory
                            from app.services.time_service import time_service

                            now = time_service.get_current_time()

                            bh = BikeHistory(
                                station=station,
                                timestamp=now,
                                available_bikes=int(item.get('capacity', 20)),
                                available_docks=0,
                                total_bikes=int(item.get('capacity', 20)),
                                total_docks=int(item.get('capacity', 20)),
                                is_station_active=True,
                                last_report_time=now,
                            )
                            db.session.add(bh)
                        except Exception:
                            # 如果无法导入 BikeHistory（模型不存在或其他原因），继续而不阻塞站点创建
                            pass
                    
                    # 每50条提交一次
                    if (imported_count + updated_count) % 50 == 0:
                        db.session.commit()
                        
                except Exception as e:
                    errors.append(f"站点 {idx+1} ({item.get('name', '未知')}) 导入失败: {str(e)}")

            db.session.commit()
            return {
                'success': True,
                'message': f'站点导入完成，新增 {imported_count} 个，更新 {updated_count} 个',
                'imported_count': imported_count,
                'updated_count': updated_count,
                'errors': errors[:10] if errors else []
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_sample_data():
        """创建示例数据（使用ISO格式）"""
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

            # 创建示例需求数据（使用ISO格式）
            sample_data = [
                {
                    "timestamp": "2025-07-01T08:00:00",  # ISO格式
                    "station_type": "canteen",
                    "weekday": 2,
                    "is_holiday": 0,
                    "weather": "晴",  # 改为中文
                    "temp": 28.4,
                    "demand": 14,
                    "station_id": station.id
                },
                {
                    "timestamp": "2025-07-01T08:15:00",  # ISO格式
                    "station_type": "canteen",
                    "weekday": 2,
                    "is_holiday": 0,
                    "weather": "雨",  # 改为中文
                    "temp": 28.6,
                    "demand": 17,
                    "station_id": station.id
                },
                {
                    "timestamp": "2025-07-01T08:30:00",  # ISO格式
                    "station_type": "canteen",
                    "weekday": 2,
                    "is_holiday": 0,
                    "weather": "多云",  # 改为中文
                    "temp": 28.8,
                    "demand": 19,
                    "station_id": station.id
                },
                {
                    "timestamp": "2025-07-01T12:00:00",  # ISO格式
                    "station_type": "canteen",
                    "weekday": 2,
                    "is_holiday": 0,
                    "weather": "晴",  # 改为中文
                    "temp": 31.5,
                    "demand": 25,
                    "station_id": station.id
                },
                {
                    "timestamp": "2025-07-01T18:00:00",  # ISO格式
                    "station_type": "dormitory",
                    "weekday": 2,
                    "is_holiday": 0,
                    "weather": "多云",  # 改为中文
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
                'message': f'成功创建 {len(sample_data)} 条示例需求数据',
                'data': sample_data
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

    @staticmethod
    def import_dispatch_tasks(tasks_data):
        """
        导入调度任务数据
        :param tasks_data: 任务数据列表或文件路径
        """
        from app.models.dispatch_task import DispatchTask
        
        # 如果是文件路径，读取文件
        if isinstance(tasks_data, str):
            if tasks_data.endswith('.json'):
                with open(tasks_data, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
            elif tasks_data.endswith('.csv'):
                import pandas as pd
                df = pd.read_csv(tasks_data)
                tasks_data = df.to_dict('records')
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for idx, task in enumerate(tasks_data):
            try:
                # 检查是否已存在相同ID的任务
                existing_task = DispatchTask.query.get(task.get('id'))
                
                if existing_task:
                    # 更新现有任务
                    existing_task.task_name = task.get('task_name', existing_task.task_name)
                    existing_task.from_station_id = task.get('from_station_id', existing_task.from_station_id)
                    existing_task.to_station_id = task.get('to_station_id', existing_task.to_station_id)
                    existing_task.bike_count = task.get('bike_count', existing_task.bike_count)
                    existing_task.priority = task.get('priority', existing_task.priority)
                    existing_task.status = task.get('status', existing_task.status)
                    existing_task.assigned_to = task.get('assigned_to', existing_task.assigned_to)
                    existing_task.created_by = task.get('created_by', existing_task.created_by)
                    existing_task.created_at = task.get('created_at', existing_task.created_at)
                    existing_task.updated_at = task.get('updated_at', existing_task.updated_at)
                    skipped_count += 1
                else:
                    # 创建新任务
                    new_task = DispatchTask(**task)
                    db.session.add(new_task)
                    imported_count += 1
                
                # 每50条提交一次
                if (imported_count + skipped_count) % 50 == 0:
                    db.session.commit()
                    
            except Exception as e:
                errors.append(f"任务 {idx+1} (ID: {task.get('id', '未知')}) 导入失败: {str(e)}")
                skipped_count += 1
        
        db.session.commit()
        
        return {
            'success': True,
            'message': f'调度任务导入完成，新增 {imported_count} 条，跳过 {skipped_count} 条',
            'imported_count': imported_count,
            'skipped_count': skipped_count,
            'errors': errors[:10] if errors else []
        }