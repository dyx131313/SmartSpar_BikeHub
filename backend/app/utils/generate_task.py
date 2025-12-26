# ==========================================================
#  file: backend/app/utils/generate_task.py   （你在的位置）
# ==========================================================
import os
import random
import pandas as pd
from datetime import datetime, timedelta
import json

class DispatchTaskGenerator:
    def __init__(self, stations_df):
        self.stations_df = stations_df
        self.status_pool   = ['pending', 'in_progress', 'completed', 'cancelled']
        self.status_weights= [45, 15, 30, 10]
        self.priority_pool = [1, 2, 3, 4, 5]
        self.priority_weights = [10, 20, 40, 20, 10]
        self.user_ids      = list(range(1, 11))

    # ------------------  生成  ------------------
    def generate(self, n=300):
        tasks, station_ids = [], self.stations_df['id'].tolist()
        for i in range(1, n + 1):
            fid, tid = random.sample(station_ids, 2)
            status   = random.choices(self.status_pool, weights=self.status_weights)[0]
            priority = random.choices(self.priority_pool, weights=self.priority_weights)[0]
            bike_cnt = random.randint(5, 50)
            assigned = random.choice(self.user_ids) if status in ('in_progress', 'completed') else None
            creator  = random.choice(self.user_ids)

            created = datetime.now() - timedelta(days=random.randint(0, 30))
            updated = created + timedelta(minutes=random.randint(10, 120)) if status == 'completed' else created

            tasks.append({
                'id': i,
                'task_name': f'调度-{bike_cnt}辆-站点{fid}→站点{tid}',
                'from_station_id': fid,
                'to_station_id': tid,
                'bike_count': bike_cnt,
                'priority': priority,
                'status': status,
                'assigned_to': assigned,
                'created_by': creator,
                'created_at': created.isoformat(timespec='seconds'),
                'updated_at': updated.isoformat(timespec='seconds')
            })
        return tasks

    # ------------------  保存  ------------------
    def save(self, out_dir, basename='api_dispatch_tasks'):
        tasks = self.generate()
        os.makedirs(out_dir, exist_ok=True)
        json_path = os.path.join(out_dir, f'{basename}.json')
        csv_path  = os.path.join(out_dir, f'{basename}.csv')

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        pd.DataFrame(tasks).to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f'调度任务已生成：\n  JSON -> {json_path}\n  CSV  -> {csv_path}')
        return json_path


# ==========================================================
#  入口 - 修正版
# ==========================================================
if __name__ == '__main__':
    # 动态计算，基于当前文件位置向上找到backend目录
    UTIL_FILE = os.path.abspath(__file__)  # .../backend/app/utils/generate_task.py
    # 向上三级：utils -> app -> backend
    BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(UTIL_FILE)))

    STATIONS_JSON = os.path.join(BACKEND_DIR, 'data', 'api_stations.json')
    
    print(f"当前脚本位置: {UTIL_FILE}")
    print(f"计算出的backend目录: {BACKEND_DIR}")
    print(f"尝试读取文件: {STATIONS_JSON}")
    
    if not os.path.exists(STATIONS_JSON):
        print(f'[ERROR] 未找到站点文件：{STATIONS_JSON}')
        print("请检查文件是否存在，或者手动指定路径")
        exit(1)

    stations_df = pd.read_json(STATIONS_JSON)
    print(f'载入 {len(stations_df)} 个站点')

    generator = DispatchTaskGenerator(stations_df)
    json_file = generator.save(out_dir=os.path.join(BACKEND_DIR, 'data'))

    print('\n=== 一键导入示例 ===')
    print(f'curl -X POST http://localhost:5000/api/dispatch-tasks/import \\\n  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\\n  -F "file=@{json_file}"')