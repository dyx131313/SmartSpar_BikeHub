import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os  # 新增：用于处理路径

class APICompatibleDataGenerator:
    def __init__(self, output_dir='../../data'):
        """
        初始化数据生成器
        
        Args:
            output_dir: 输出目录，相对于脚本位置
        """
        # 确保输出目录存在
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建输出目录: {output_dir}")
        
        # 真点位坐标池（经纬度 + 类型 + 基础名）
        self.real_points = {
            'canteen': [
                (31.287659152883148, 121.2169606897436, '大食堂'),
                (31.28755530532723, 121.21803411705396, '小食堂'),
                (31.28764400845209, 121.21988223501046, '星巴克'),
                (31.287862520680598, 121.22272783016359, '嘉实广场')
            ],
            'library': [
                (31.28689511868011, 121.21198518888175, '图书馆'),
                (31.290188169848914, 121.21632920087872, '体育中心'),
                (31.2881320399035, 121.21502284086417, '校医院')
            ],
            'teaching_building': [
                (31.28552442349322, 121.21551264834397, '复楼'),
                (31.2857213803124, 121.21412679833715, '安楼'),
                (31.287957847891327, 121.21279250074315, '智信馆'),
                (31.282950989439797, 121.21426932551475, '济事楼')
            ],
            'dormitory': [
                (31.285962392702352, 121.21727756019918, '宿舍区1号'),
                (31.289481334451224, 121.2178783301961, '宿舍区2号'),
                (31.289898166569664, 121.22023965865807, '宿舍区3号'),
                (31.281397287919805, 121.2105397883872, '天骄公寓')
            ],
            'gate': [
                (31.282353959967587, 121.21206024850576, '南门'),
                (31.28527198186722, 121.20751354387971, '西门'),
                (31.282619862470163, 121.22152308156367, '东门'),
                (31.29140417777084, 121.21772982961366, '北门')
            ]
        }
        
    def generate_stations(self, num_stations=60):
        stations = []
        type_list = list(self.real_points.keys())
        # 先把所有真点位铺平，按顺序占用前 N 个 ID
        real_flat = [(t, lat, lng, base_name)
                     for t in type_list for lat, lng, base_name in self.real_points[t]]
        for idx, (st_type, lat, lng, base_name) in enumerate(real_flat):
            stations.append(self._make_station_dict(
                id=idx + 1,
                name=base_name,
                station_type=st_type,
                lat=lat,   # 真实坐标不抖动，保持原始坐标
                lng=lng
            ))

        # 剩余站点：随机挑一个母点，做较小抖动，命名"母名+序号"
        counter = {base_name: 1 for _, _, _, base_name in real_flat}
        for idx in range(len(real_flat) + 1, num_stations + 1):
            st_type, lat, lng, base_name = random.choice(real_flat)
            new_lat = lat + random.uniform(-0.005, 0.005)  # 缩小抖动范围，保持在校园内
            new_lng = lng + random.uniform(-0.005, 0.005)
            seq = counter[base_name]
            counter[base_name] += 1
            stations.append(self._make_station_dict(
                id=idx,
                name=f"{base_name}{seq}号点",
                station_type=st_type,
                lat=new_lat,
                lng=new_lng
            ))
        return pd.DataFrame(stations)

    def _make_station_dict(self, id, name, station_type, lat, lng):
        return {
            'id': id,
            'name': name,
            'station_type': station_type,
            'latitude':  lat,   # 或者 round(lat, 12)
            'longitude': lng,
            'capacity': random.randint(20, 60),
            'description': self.generate_description(name, station_type),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    def generate_description(self, name, station_type):
        """生成站点描述"""
        descriptions = {
            'canteen': f"{name}门口共享单车停放点，用餐高峰期需求较大",
            'library': f"{name}学习区域单车停放点，学习时段需求集中",
            'teaching_building': f"{name}教学区域单车停放点，上下课时段流量大",
            'dormitory': f"{name}生活区域单车停放点，早晚出行需求集中",
            'gate': f"{name}出入口单车停放点，进出校园主要通道"
        }
        return descriptions.get(station_type, f"{name}共享单车停放点")
    
    def generate_demand_data(self, stations_df, days=100):
        """生成符合API接口的需求数据"""
        demands = []
        
        # 根据DemandData模型需要的天气类型
        weather_types = ['晴', '多云', '阴', '雨', '雪']
        weather_weights = [0.4, 0.3, 0.15, 0.1, 0.05]
        
        # 温度范围（上海嘉定）
        temp_range = (-5, 35)
        
        current_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            date = current_date + timedelta(days=day)
            is_weekday = date.weekday() < 5
            is_holiday = self.is_holiday(date)
            weather = random.choices(weather_types, weights=weather_weights)[0]
            temp = round(random.uniform(*temp_range), 1)
            
            for station in stations_df.to_dict('records'):
                for hour in range(24):
                    # 生成需求数量（基于站点类型和时间）
                    base_demand = self.calculate_base_demand(
                        station['station_type'], hour, is_weekday, is_holiday, weather
                    )
                    
                    # 添加随机波动
                    demand = max(1, int(base_demand * random.uniform(0.8, 1.2)))
                    
                    # 生成符合DemandData模型的记录
                    timestamp = date.replace(hour=hour, minute=0, second=0)
                    
                    demand_record = {
                        # 关键字段
                        'timestamp': timestamp.isoformat(),  # ISO格式
                        'station_id': station['id'],
                        'station_type': station['station_type'],
                        'weekday': date.weekday() + 1,  # 1-7
                        'is_holiday': is_holiday,
                        'weather': weather,
                        'temp': temp,
                        'demand': demand,
                        # 可选字段（根据你的DemandData模型）
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    demands.append(demand_record)
                    
        return pd.DataFrame(demands)
    
    def calculate_base_demand(self, station_type, hour, is_weekday, is_holiday, weather):
        """计算基础需求数量"""
        # 基础需求矩阵 [station_type][hour]
        base_matrix = {
            'canteen': [2,1,1,1,2,5,15,12,8,6,20,25,30,15,8,10,25,30,20,12,8,5,3,2],
            'library': [1,1,1,1,2,3,8,15,20,25,18,15,12,10,8,12,18,22,25,20,15,10,5,3],
            'teaching_building': [1,1,1,1,2,4,20,25,30,25,20,18,15,12,10,15,20,25,20,15,10,5,3,2],
            'dormitory': [3,2,2,2,3,8,25,15,8,5,4,4,4,4,5,8,15,20,25,20,15,10,8,5],
            'gate': [2,1,1,1,2,5,20,15,10,8,6,5,5,5,6,8,12,15,12,10,8,6,4,3]
        }
        
        base = base_matrix.get(station_type, [5]*24)[hour]
        
        # ③ 高峰期集中放大
        if is_weekday and hour in (7, 8, 9, 11, 12, 13, 17, 18, 19):
            base *= 3

        # 调整因子
        if not is_weekday:
            base *= 0.7  # 周末需求减少
        if is_holiday:
            base *= 0.5  # 节假日需求大幅减少
        if weather == '雨':
            base *= 0.6  # 雨天需求减少
        elif weather == '晴':
            base *= 1.2  # 晴天需求增加
        elif weather == '雪':
            base *= 0.4  # 雪天需求大幅减少
            
        return base
    
    def is_holiday(self, date):
        """判断是否为节假日"""
        # 简单节假日判断（可扩展）
        month_day = (date.month, date.day)
        holidays = [
            (1, 1),   # 元旦
            (1, 22), (1, 23), (1, 24),  # 春节
            (4, 5),   # 清明节
            (5, 1),   # 劳动节
            (6, 22),  # 端午节
            (9, 29), (9, 30),  # 中秋节
            (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6)  # 国庆节
        ]
        return month_day in holidays or date.weekday() >= 5  # 周末也算节假日
    
    def generate_demand_data_for_api(self, stations_df, days=30):
        """生成专门用于API导入的DEMAND数据（简化版，减少数据量）"""
        demands = []
        
        weather_types = ['晴', '多云', '阴', '雨', '雪']
        weather_weights = [0.4, 0.3, 0.15, 0.1, 0.05]
        
        current_date = datetime.now() - timedelta(days=days)
        
        print(f"开始生成需求数据，时间范围：{current_date.date()} 到 {datetime.now().date()}")
        
        # 为了减少数据量，每个站点每天只生成3个关键时间点（早高峰、午高峰、晚高峰）
        for station in stations_df.to_dict('records'):
            station_id = station['id']
            station_type = station['station_type']
            
            for day_offset in range(days):
                date = current_date + timedelta(days=day_offset)
                is_holiday = self.is_holiday(date)
                weather = random.choices(weather_types, weights=weather_weights)[0]
                temp = round(random.uniform(-5, 35), 1)
                
                # 每天3个关键时间点：8点（早高峰）、12点（午高峰）、18点（晚高峰）
                for hour in [8, 12, 18]:
                    timestamp = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    
                    # 计算需求
                    base_demand = self.calculate_base_demand(
                        station_type, hour, date.weekday() < 5, is_holiday, weather
                    )
                    demand = max(1, int(base_demand * random.uniform(0.8, 1.2)))
                    
                    demands.append({
                        'timestamp': timestamp.isoformat(),
                        'station_id': station_id,
                        'station_type': station_type,
                        'weekday': date.weekday() + 1,
                        'is_holiday': is_holiday,
                        'weather': weather,
                        'temp': temp,
                        'demand': demand
                    })
        
        print(f"生成 {len(demands)} 条需求记录")
        return pd.DataFrame(demands)
    
    def save_to_file(self, filename, data):
        """保存数据到文件"""
        filepath = os.path.join(self.output_dir, filename)
        
        if isinstance(data, pd.DataFrame):
            # 保存为JSON
            json_path = filepath.replace('.csv', '.json')
            data.to_json(json_path, orient='records', force_ascii=False, indent=2)
            
            # 同时保存为CSV备用
            csv_path = filepath.replace('.json', '.csv')
            data.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            print(f"  JSON: {json_path}")
            print(f"  CSV:  {csv_path}")
        else:
            # 如果是字典列表，直接保存为JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  {filepath}")
        
        return filepath

def main():
    # 设置输出目录为项目根目录下的data文件夹
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(script_dir)
    project_root = os.path.dirname(app_dir)  # ✅ 再跳一级
    data_dir = os.path.join(project_root, 'data')
    
    print("开始生成符合API接口的数据...")
    print(f"脚本位置: {script_dir}")
    print(f"数据输出目录: {data_dir}")
    
    generator = APICompatibleDataGenerator(output_dir=data_dir)
    
    # 生成站点数据
    print("\n1. 生成站点数据...")
    stations_df = generator.generate_stations()     # 用默认值
    print(f"生成 {len(stations_df)} 个站点")
    print(f"站点类型分布: {stations_df['station_type'].value_counts().to_dict()}")
    
    # 生成需求数据（简化版，用于API导入）
    print("\n2. 生成需求数据...")
    demands_df = generator.generate_demand_data_for_api(stations_df, days=30)  # 减少天数以降低数据量
    
    # 检查数据格式
    print("\n=== 数据格式检查 ===")
    sample_record = demands_df.iloc[0].to_dict()
    print(f"示例记录字段: {list(sample_record.keys())}")
    print(f"timestamp格式: {sample_record['timestamp']}")
    print(f"station_id类型: {type(sample_record['station_id'])}")
    print(f"demand类型: {type(sample_record['demand'])}")
    
    # 保存为JSON格式（符合API导入格式）
    print("\n3. 保存数据文件...")
    
    # 保存站点数据
    stations_json = stations_df.to_dict('records')
    stations_file = generator.save_to_file('api_stations.json', stations_json)
    
    # 保存需求数据
    demands_json = demands_df.to_dict('records')
    # 如果需要完整数据，可以去掉这个限制
    #if len(demands_json) > 1000:
     #   print(f"需求数据较多({len(demands_json)}条)，只保存前1000条用于测试")
     #   demands_json = demands_json[:1000]
    
    demands_file = generator.save_to_file('api_demands.json', demands_json)
    
    print("\n=== 文件生成完成 ===")
    print(f"站点数据: {len(stations_json)}条")
    print(f"需求数据: {len(demands_json)}条")
    print(f"需求数据时间范围: {demands_df['timestamp'].min()} 到 {demands_df['timestamp'].max()}")
    
    # 获取完整路径
    stations_full_path = os.path.abspath(stations_file)
    demands_full_path = os.path.abspath(demands_file)
    
    print("\n=== 文件完整路径 ===")
    print(f"站点数据: {stations_full_path}")
    print(f"需求数据: {demands_full_path}")
    
    # 提供API调用示例
    print("\n=== API调用示例 ===")
    print(f"""
# 1. 先导入站点数据
curl -X POST http://localhost:5000/api/stations \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d @{demands_full_path}

# 2. 导入需求数据
curl -X POST http://localhost:5000/api/demand-data \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d @{demands_full_path}

# 3. 或者使用文件上传方式导入需求数据
curl -X POST http://localhost:5000/api/demand-data/import \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -F "file=@{demands_full_path}"
    """)

if __name__ == "__main__":
    main()