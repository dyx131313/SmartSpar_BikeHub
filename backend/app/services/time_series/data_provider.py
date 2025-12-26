import json
import torch
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler, LabelEncoder
import os
from datetime import timedelta


class BikeDemandDataset(Dataset):
    def __init__(self, data, seq_len, pred_len, flag="train", split_ratio=0.8):
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.flag = flag
        self.split_ratio = split_ratio

        # Data preprocessing
        self.__read_data__(data)

    def __read_data__(self, df_raw):
        # df_raw is already a DataFrame

        # Sort by timestamp just in case
        df_raw = df_raw.sort_values(by=["station_id", "timestamp"]).reset_index(
            drop=True
        )

        self.data_x = []
        self.data_y = []
        self.data_stamp = []

        # Preprocessing

        timestamps = df_raw["timestamp"].unique()
        timestamps.sort()
        split_idx = int(len(timestamps) * self.split_ratio)
        train_dates = timestamps[:split_idx]
        test_dates = timestamps[split_idx:]

        if self.flag == "train":
            df_data = df_raw[df_raw["timestamp"].isin(train_dates)].copy()
        else:
            df_data = df_raw[df_raw["timestamp"].isin(test_dates)].copy()

        # We need to organize data by station to form sequences
        grouped = df_data.groupby("station_id")

        # Features to use
        # Numerical: temp, demand (target)
        # Categorical: station_type, weekday, is_holiday, weather
        pass


class DataProvider:
    def __init__(self, json_path, seq_len, pred_len, split_ratio=0.8):
        self.json_path = json_path
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.split_ratio = split_ratio

        self.scalers = {}
        self.encoders = {}

        self.load_and_process()

    def load_and_process(self):
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        # Convert timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Sort
        df = df.sort_values(by=["station_id", "timestamp"]).reset_index(drop=True)

        # Encode Categorical
        cat_cols = ["station_type", "weather"]
        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.encoders[col] = le

        # Boolean to int
        df["is_holiday"] = df["is_holiday"].astype(int)

        # Normalize Numerical

        timestamps = df["timestamp"].unique()
        timestamps.sort()
        split_len = int(len(timestamps) * self.split_ratio)
        train_cutoff = timestamps[split_len]

        train_df = df[df["timestamp"] < train_cutoff]

        num_cols = ["temp", "demand"]
        scaler = StandardScaler()
        scaler.fit(train_df[num_cols])

        df[num_cols] = scaler.transform(df[num_cols])
        self.scaler = scaler

        self.data = df
        self.train_cutoff = train_cutoff

        # Feature columns
        self.feature_cols = [
            "demand",
            "temp",
            "weekday",
            "is_holiday",
            "station_type",
            "weather",
        ]
        # Target column index (demand is 0 in feature_cols)
        self.target_col_idx = 0

    def get_dataset(self, flag="train"):
        # Pass the full dataframe and let TimeSeriesDataset handle the splitting logic
        # to ensure test set has enough lookback window
        return TimeSeriesDataset(
            self.data,
            self.seq_len,
            self.pred_len,
            self.feature_cols,
            flag,
            self.train_cutoff,
        )

    def get_last_window(self):
        # Get the last seq_len data points for each station to predict future
        # We return a dict {station_id: {'data': numpy_array, 'last_timestamp': timestamp}}
        last_windows = {}
        for station_id, group in self.data.groupby("station_id"):
            if len(group) >= self.seq_len:
                last_windows[station_id] = {
                    "data": group[self.feature_cols].values[-self.seq_len :],
                    "last_timestamp": group["timestamp"].iloc[-1],
                }
        return last_windows

    def inverse_transform(self, data):
        dummy = np.zeros((data.size, 2))
        dummy[:, 0] = data.flatten()  # demand is 0th

        inv = self.scaler.inverse_transform(dummy)
        return inv[:, 0].reshape(data.shape)

    def generate_future_timestamps(self, start_time, steps):
        # Generate future timestamps based on the 6-point daily schedule
        # 06:00, 10:00, 14:00, 18:00, 20:00, 22:00
        schedule_hours = [6, 10, 14, 18, 20, 22]
        future_timestamps = []

        current_time = start_time
        for _ in range(steps):
            # Find next scheduled time
            found = False
            # Check today's remaining hours
            for h in schedule_hours:
                candidate = current_time.replace(
                    hour=h, minute=0, second=0, microsecond=0
                )
                if candidate > current_time:
                    current_time = candidate
                    found = True
                    break

            if not found:
                # Move to next day first hour
                current_time = (current_time + timedelta(days=1)).replace(
                    hour=schedule_hours[0], minute=0, second=0, microsecond=0
                )

            future_timestamps.append(current_time.isoformat())

        return future_timestamps


class TimeSeriesDataset(Dataset):
    def __init__(self, df, seq_len, pred_len, feature_cols, flag, train_cutoff):
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.feature_cols = feature_cols

        self.x = []
        self.y = []

        # Group by station to create sequences
        for station_id, group in df.groupby("station_id"):
            # We need to filter based on flag and train_cutoff
            # But we need to be careful about the window

            # Get all timestamps for this station
            timestamps = group["timestamp"].values
            values = group[feature_cols].values

            total_len = len(values)
            if total_len < seq_len + pred_len:
                continue

            for i in range(total_len - seq_len - pred_len + 1):
                # Window: x = [i : i+seq_len], y = [i+seq_len : i+seq_len+pred_len]
                # The timestamp of the first point of y is timestamps[i+seq_len]

                y_start_time = timestamps[i + seq_len]

                if flag == "train":
                    # If y starts before cutoff, it's train
                    if y_start_time < train_cutoff:
                        self.x.append(values[i : i + seq_len])
                        self.y.append(values[i + seq_len : i + seq_len + pred_len])
                else:
                    # If y starts at or after cutoff, it's test
                    if y_start_time >= train_cutoff:
                        self.x.append(values[i : i + seq_len])
                        self.y.append(values[i + seq_len : i + seq_len + pred_len])

        self.x = np.array(self.x)
        self.y = np.array(self.y)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return torch.FloatTensor(self.x[idx]), torch.FloatTensor(self.y[idx])
