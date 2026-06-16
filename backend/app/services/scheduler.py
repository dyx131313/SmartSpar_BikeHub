import threading
import time
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.models.demand_data import DemandData
from app.models.station import Station
from app.config.paths import Paths
from app.services.prediction_registry import prediction_model_registry
from app.services.time_service import time_service
from sklearn.preprocessing import StandardScaler, LabelEncoder


class BikeScheduler:
    def __init__(self, app=None):
        self.app = app
        self.stop_event = threading.Event()
        self.thread = None
        self.last_run_hour = None
        self.prediction_status = (
            {}
        )  # {model_name: {status: str, progress: int, message: str}}

        # 缓存编码器和缩放器，避免每次都重新拟合导致抖动
        # 在实际生产中，这些应该从训练好的文件中加载
        self.scalers = {}
        self.encoders = {}
        self.feature_cols = [
            "demand",
            "temp",
            "weekday",
            "is_holiday",
            "station_type",
            "weather",
        ]

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self._run_loop)
            self.thread.daemon = True
            self.thread.start()
            print("BikeScheduler started.")

    def _run_loop(self):
        # 如果没有传入app，创建一个上下文
        if not self.app:
            from app import create_app

            self.app = create_app()

        with self.app.app_context():
            while not self.stop_event.is_set():
                try:
                    current_time = time_service.get_current_time()
                    current_hour_str = current_time.strftime("%Y-%m-%d %H:00:00")

                    # 检查是否进入了新的小时
                    if self.last_run_hour != current_hour_str:
                        print(
                            f"New hour detected: {current_hour_str}. Running prediction cycle..."
                        )
                        self.run_prediction_cycle(current_time)
                        self.last_run_hour = current_hour_str

                    # 每10秒检查一次 (为了响应真实时间的流逝)
                    time.sleep(10)
                except Exception as e:
                    print(f"Error in scheduler loop: {e}")
                    time.sleep(60)

    def run_prediction_cycle(self, current_time, model_name=None):
        """运行预测循环"""
        # 确保在应用上下文中运行
        if not self.app:
            from app import create_app

            self.app = create_app()

        with self.app.app_context():
            models = [model_name] if model_name else prediction_model_registry.names()

            # 初始化状态
            for m in models:
                self.prediction_status[m] = {
                    "status": "running",
                    "progress": 0,
                    "message": "Starting...",
                }

            try:
                # 1. 准备数据
                # 我们需要过去96小时的数据作为输入 (seq_len=96)
                # 为了拟合Scaler，我们多取一些数据，比如过去60天 (增加回溯时间以应对数据稀疏)
                lookback_days = 60
                start_time = current_time - timedelta(days=lookback_days)

                print(f"Fetching data from {start_time} to {current_time}")
                for m in models:
                    self.prediction_status[m] = {
                        "status": "running",
                        "progress": 10,
                        "message": "Fetching data...",
                    }

                # 从数据库获取数据
                # 注意：这里假设数据库中已经有了直到 current_time 的数据
                # 在真实场景中，可能需要处理数据延迟或缺失的情况
                records = (
                    DemandData.query.filter(
                        DemandData.timestamp >= start_time,
                        DemandData.timestamp <= current_time,
                    )
                    .order_by(DemandData.timestamp)
                    .all()
                )

                if not records:
                    print("No data found for prediction.")
                    for m in models:
                        self.prediction_status[m] = {
                            "status": "failed",
                            "progress": 0,
                            "message": "No data found",
                        }
                    return

                print(f"Found {len(records)} records.")
                df = pd.DataFrame([r.to_dict() for r in records])
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                # 确保数据按站点和时间排序
                df = df.sort_values(by=["station_id", "timestamp"])

                # 打印每个站点的数据量
                station_counts = df.groupby("station_id").size()
                print("Records per station (raw):")
                print(station_counts)

                # 数据填充：重采样为每小时数据并前向填充
                # 这解决了数据稀疏（如每4小时一条）和数据中断的问题
                print("Resampling and filling data...")
                full_df_list = []
                for station_id, group in df.groupby("station_id"):
                    # 去除重复的时间戳，保留最后一条
                    group = group.drop_duplicates(subset=["timestamp"], keep="last")

                    # 设置时间索引
                    group = group.set_index("timestamp")
                    # 重采样到小时级，并填充缺失值
                    # 1. resample('H').asfreq() 创建小时级网格
                    # 2. ffill() 前向填充（用最近的过去值填充）
                    # 3. bfill() 后向填充（处理开头缺失）
                    resampled = group.resample("H").ffill().bfill()

                    # 确保时间范围覆盖到 current_time
                    # 如果数据在 current_time 之前就断了，我们需要扩展它
                    if resampled.index.max() < current_time:
                        # 创建一个直到 current_time 的索引
                        extended_index = pd.date_range(
                            start=resampled.index.min(), end=current_time, freq="H"
                        )
                        resampled = resampled.reindex(extended_index).ffill()

                    resampled = resampled.reset_index()
                    # 确保时间戳列名为 timestamp
                    if (
                        "timestamp" not in resampled.columns
                        and "index" in resampled.columns
                    ):
                        resampled = resampled.rename(columns={"index": "timestamp"})

                    resampled["station_id"] = station_id  # 确保 station_id 存在
                    full_df_list.append(resampled)

                if full_df_list:
                    df = pd.concat(full_df_list, ignore_index=True)
                    print("Records per station (after resampling):")
                    print(df.groupby("station_id").size())
                else:
                    print("No data after resampling.")

                # 2. 预处理数据 (模拟 DataProvider 的逻辑)
                for m in models:
                    self.prediction_status[m] = {
                        "status": "running",
                        "progress": 30,
                        "message": "Preprocessing data...",
                    }
                processed_df = self._preprocess_data(df)

                # 3. 对每个模型进行预测
                for model_name in models:
                    try:
                        self.prediction_status[model_name] = {
                            "status": "running",
                            "progress": 50,
                            "message": "Loading model...",
                        }
                        self._predict_for_model(model_name, processed_df, current_time)
                        self.prediction_status[model_name] = {
                            "status": "completed",
                            "progress": 100,
                            "message": "Done",
                        }
                    except Exception as e:
                        print(f"Error predicting for {model_name}: {e}")
                        self.prediction_status[model_name] = {
                            "status": "failed",
                            "progress": 0,
                            "message": str(e),
                        }
            except Exception as e:
                print(f"Error in prediction cycle: {e}")
                for m in models:
                    self.prediction_status[m] = {
                        "status": "failed",
                        "progress": 0,
                        "message": str(e),
                    }

    def _preprocess_data(self, df):
        """预处理数据：编码和缩放"""
        df_copy = df.copy()

        # 编码分类变量
        cat_cols = ["station_type", "weather"]
        for col in cat_cols:
            if col not in self.encoders:
                self.encoders[col] = LabelEncoder()
                # 拟合所有可能的值
                self.encoders[col].fit(df_copy[col].astype(str))

            # 处理未知标签
            # 简单起见，这里假设所有标签都见过。生产环境需要更健壮的处理
            try:
                df_copy[col] = self.encoders[col].transform(df_copy[col].astype(str))
            except ValueError:
                # 如果遇到新标签，重新拟合 (简化处理)
                self.encoders[col].fit(df_copy[col].astype(str))
                df_copy[col] = self.encoders[col].transform(df_copy[col].astype(str))

        # 转换布尔值
        df_copy["is_holiday"] = df_copy["is_holiday"].astype(int)

        # 缩放数值变量
        num_cols = ["temp", "demand"]
        if "scaler" not in self.scalers:
            self.scalers["scaler"] = StandardScaler()
            self.scalers["scaler"].fit(df_copy[num_cols])

        df_copy[num_cols] = self.scalers["scaler"].transform(df_copy[num_cols])

        return df_copy

    def _predict_for_model(self, model_name, df, current_time):
        """为特定模型运行预测"""
        print(f"Running prediction for {model_name}...")

        # 加载模型
        try:
            from app.services.time_series.inference import TimeSeriesInference

            inference = TimeSeriesInference(
                model_name,
                checkpoint_dir=str(Paths.MODEL_CHECKPOINTS),
            )
        except ImportError as e:
            print(
                "Time series dependencies are not installed. "
                "Install the optional torch stack before running prediction jobs."
            )
            raise RuntimeError(f"预测依赖未安装: {e}") from e
        except Exception as e:
            print(f"Could not load model {model_name}: {e}")
            return

        seq_len = 96  # 假设所有模型都用96

        future_results = []

        # 按站点分组预测
        for station_id, group in df.groupby("station_id"):
            if len(group) < seq_len:
                print(
                    f"Station {station_id} has insufficient data: {len(group)} < {seq_len}"
                )
                continue

            print(f"Predicting for station {station_id} with {len(group)} records")

            # Debug: 打印列名以排查 'timestamp' KeyError
            if "timestamp" not in group.columns:
                print(
                    f"Warning: 'timestamp' not found in columns. Columns are: {group.columns}"
                )
                # 尝试从索引获取
                if group.index.name == "timestamp":
                    group = group.reset_index()
                elif "index" in group.columns:
                    group = group.rename(columns={"index": "timestamp"})

            # 取最后 seq_len 条数据
            input_seq = group[self.feature_cols].values[-seq_len:]

            # 增加 Batch 维度 [1, Seq_Len, Channels]
            input_data = input_seq[np.newaxis, :, :]

            # 预测
            output = inference.predict(input_data)
            # output shape: [1, Pred_Len, Channels]

            # 反归一化
            # output[:, :, 0] 是 demand (因为 demand 是 feature_cols 的第0个)
            # 我们需要构建一个 dummy array 来反归一化
            pred_len = output.shape[1]
            dummy = np.zeros((pred_len, 2))  # 2 是 num_cols 的长度 (temp, demand)
            # 注意：scaler 是 fit 在 [temp, demand] 上的
            # 但是 feature_cols 是 [demand, temp, ...]
            # 这是一个潜在的坑。我们需要检查 DataProvider 的逻辑。
            # DataProvider: num_cols = ["temp", "demand"]
            # DataProvider.inverse_transform: dummy[:, 0] = data.flatten() -> 这看起来它是把 demand 放在第0列反归一化？
            # 让我们看 DataProvider.inverse_transform:
            # dummy = np.zeros((data.size, 2))
            # dummy[:, 0] = data.flatten()
            # inv = self.scaler.inverse_transform(dummy)
            # 这意味着它假设 scaler 的第0列是 demand？
            # 但是 scaler.fit(train_df[num_cols]) 其中 num_cols=["temp", "demand"]
            # 所以 scaler 的第0列是 temp，第1列是 demand。
            # DataProvider 的 inverse_transform 看起来有 bug 或者我理解错了。
            # 让我们再看一眼 DataProvider.inverse_transform
            # dummy[:, 0] = data.flatten() -> 赋值给 temp?
            # inv = ... -> inv[:, 0] -> 取回 temp?
            # 如果 output 是 demand，那应该赋值给 dummy[:, 1] (如果 demand 是第1列)

            # 为了安全起见，我按照 scaler 的定义来做：
            # scaler fit on ["temp", "demand"]
            # output 包含所有 channels (c_out=6)
            # 假设模型的输出顺序和输入特征顺序一致：[demand, temp, weekday, ...]
            # 那么 output[:, :, 0] 是 demand, output[:, :, 1] 是 temp

            pred_demand_scaled = output[0, :, 0]
            pred_temp_scaled = output[0, :, 1]

            # 构建用于 inverse_transform 的数组
            # scaler expects [temp, demand]
            inv_input = np.column_stack((pred_temp_scaled, pred_demand_scaled))
            inv_output = self.scalers["scaler"].inverse_transform(inv_input)

            # inv_output[:, 1] 是 demand
            real_demand = inv_output[:, 1]

            # 构建结果
            base_time = group.iloc[-1]["timestamp"]

            station_predictions = []
            for i, val in enumerate(real_demand):
                future_time = base_time + timedelta(hours=i + 1)
                station_predictions.append(
                    {
                        "timestamp": future_time.isoformat(),
                        "demand": max(0, round(float(val))),
                    }
                )

            future_results.append(
                {"station_id": int(station_id), "predictions": station_predictions}
            )

        # 保存结果到文件
        save_path = Paths.model_file(model_name, "future.json")

        with save_path.open("w", encoding="utf-8") as f:
            json.dump(future_results, f, ensure_ascii=False, indent=2)

        print(f"Saved predictions for {model_name} to {save_path}")


# 全局实例
scheduler = BikeScheduler()
