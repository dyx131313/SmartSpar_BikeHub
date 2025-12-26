"""
需求预测服务
集成机器学习模型进行单车需求预测
"""

import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import os
from typing import Dict, List, Tuple, Any, Optional
import logging

# 机器学习模型 - 无需GPU
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class BikeDemandPredictor:
    """单车需求预测器服务"""

    def __init__(self, model_path: str = "app/services/models/demand_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.models = {
            'rf': RandomForestRegressor(n_estimators=100, random_state=42),
            'gb': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'ridge': Ridge(alpha=1.0),
            'dt': DecisionTreeRegressor(random_state=42)
        }
        self.best_model_name = None
        self.is_trained = False

    def load_data(self, csv_path: str) -> pd.DataFrame:
        """加载训练数据"""
        logger.info(f"正在加载数据: {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info(f"数据形状: {df.shape}")
        return df

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据预处理和特征工程"""
        logger.info("正在进行数据预处理...")

        # 复制数据避免修改原始数据
        df = df.copy()

        # 处理时间特征
        df['date'] = pd.to_datetime(df['date'])
        df['hour'] = df['date'].dt.hour
        df['day'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year

        # 创建时间周期特征
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['weekday_sin'] = np.sin(2 * np.pi * df['weekday'] / 7)
        df['weekday_cos'] = np.cos(2 * np.pi * df['weekday'] / 7)

        # 创建温度区间特征
        df['temp_range'] = pd.cut(df['temp'], bins=5, labels=[0,1,2,3,4])
        df['temp_range'] = df['temp_range'].astype(float)

        # 创建交互特征
        df['station_temp'] = df['station_type'] * df['temp']
        df['hour_station'] = df['hour'] * df['station_type']
        df['weather_station'] = df['weather'] * df['station_type']

        # 周末和工作日标记
        df['is_weekend'] = (df['weekday'] >= 5).astype(int)

        # 高峰时段标记 (7-9点, 17-19点)
        df['is_rush_hour'] = ((df['hour'].between(7, 9)) | (df['hour'].between(17, 19))).astype(int)

        logger.info("特征工程完成")
        return df

    def prepare_features(self, df: pd.DataFrame, is_training: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """准备特征和目标变量"""
        # 选择特征列
        feature_cols = [
            'station_type', 'temp', 'is_holiday', 'weather', 'weekday',
            'hour', 'day', 'month', 'hour_sin', 'hour_cos',
            'weekday_sin', 'weekday_cos', 'temp_range', 'station_temp',
            'hour_station', 'weather_station', 'is_weekend', 'is_rush_hour'
        ]

        if is_training:
            self.feature_columns = feature_cols

        X = df[feature_cols].values
        y = df['demand'].values if 'demand' in df.columns else None

        # 特征标准化
        if is_training:
            X = self.scaler.fit_transform(X)
        else:
            X = self.scaler.transform(X)

        return X, y

    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """训练多个模型并选择最佳模型"""
        logger.info("开始训练模型...")

        # 分割训练集和验证集
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        results = {}

        for name, model in self.models.items():
            logger.info(f"训练 {name} 模型...")

            # 训练模型
            model.fit(X_train, y_train)

            # 验证集预测
            y_pred = model.predict(X_val)

            # 计算评估指标
            mae = mean_absolute_error(y_val, y_pred)
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            r2 = r2_score(y_val, y_pred)

            results[name] = {
                'mae': mae,
                'rmse': rmse,
                'r2': r2,
                'model': model
            }

            logger.info(f"{name}: MAE={mae:.2f}, RMSE={rmse:.2f}, R2={r2:.3f}")

        # 选择最佳模型 (基于MAE)
        best_name = min(results.keys(), key=lambda x: results[x]['mae'])
        self.best_model_name = best_name
        self.model = results[best_name]['model']

        # 使用全部数据重新训练最佳模型
        logger.info(f"使用全部数据重新训练最佳模型: {best_name}")
        self.model.fit(X, y)

        self.is_trained = True
        return results

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """预测单个样本的需求量"""
        if not self.is_trained:
            raise ValueError("模型尚未训练，请先调用train方法")

        try:
            # 将输入数据转换为DataFrame
            df = pd.DataFrame([input_data])

            # 预处理
            df = self.preprocess_data(df)

            # 准备特征
            X, _ = self.prepare_features(df, is_training=False)

            # 预测
            prediction = self.model.predict(X)[0]
            prediction_value = max(0, int(prediction))  # 确保预测值为非负整数

            return {
                'prediction': prediction_value,
                'confidence': self._calculate_confidence(input_data),
                'model_type': self.best_model_name,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"预测过程中出错: {e}")
            raise

    def predict_batch(self, input_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量预测"""
        if not self.is_trained:
            raise ValueError("模型尚未训练，请先调用train方法")

        try:
            df = pd.DataFrame(input_data_list)
            df = self.preprocess_data(df)
            X, _ = self.prepare_features(df, is_training=False)
            predictions = self.model.predict(X)

            results = []
            for i, (input_data, prediction) in enumerate(zip(input_data_list, predictions)):
                prediction_value = max(0, int(prediction))
                results.append({
                    'prediction': prediction_value,
                    'confidence': self._calculate_confidence(input_data),
                    'model_type': self.best_model_name,
                    'timestamp': datetime.now().isoformat(),
                    'input_index': i
                })

            return results

        except Exception as e:
            logger.error(f"批量预测过程中出错: {e}")
            raise

    def _calculate_confidence(self, input_data: Dict[str, Any]) -> float:
        """计算预测置信度"""
        # 基于特征相似性和历史数据计算置信度
        # 这里使用简化的置信度计算方法
        base_confidence = 0.85

        # 根据时间特征调整置信度
        try:
            hour = pd.to_datetime(input_data['date']).hour
            if 7 <= hour <= 9 or 17 <= hour <= 19:  # 高峰时段
                base_confidence += 0.05
            elif hour < 6 or hour > 22:  # 深夜时段
                base_confidence -= 0.1
        except:
            pass

        # 根据天气调整置信度
        weather = input_data.get('weather', 0)
        if weather == 3:  # 晴天
            base_confidence += 0.03
        elif weather == 2:  # 雨雪天
            base_confidence -= 0.05

        return max(0.1, min(0.99, base_confidence))

    def save_model(self) -> None:
        """保存模型和预处理器"""
        if not self.is_trained:
            raise ValueError("模型尚未训练")

        # 确保目录存在
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'best_model_name': self.best_model_name,
            'is_trained': self.is_trained,
            'training_date': datetime.now().isoformat()
        }

        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info(f"模型已保存到: {self.model_path}")

    def load_model(self) -> None:
        """加载已保存的模型"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"模型文件不存在: {self.model_path}")

        with open(self.model_path, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.best_model_name = model_data['best_model_name']
        self.is_trained = model_data['is_trained']

        logger.info(f"模型已从 {self.model_path} 加载")

    def train(self, csv_path: str) -> Dict[str, Any]:
        """完整的训练流程"""
        try:
            # 加载数据
            df = self.load_data(csv_path)

            # 数据预处理
            df = self.preprocess_data(df)

            # 准备特征
            X, y = self.prepare_features(df, is_training=True)

            # 训练模型
            results = self.train_models(X, y)

            # 保存模型
            self.save_model()

            # 提取训练结果摘要
            training_summary = {}
            for name, metrics in results.items():
                if isinstance(metrics, dict) and 'mae' in metrics:
                    training_summary[name] = {
                        'mae': metrics['mae'],
                        'rmse': metrics['rmse'],
                        'r2': metrics['r2']
                    }

            return {
                'best_model': self.best_model_name,
                'training_results': training_summary,
                'feature_columns': self.feature_columns,
                'training_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"训练过程中出错: {e}")
            raise

    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        if not self.is_trained:
            raise ValueError("模型尚未训练")

        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            return dict(zip(self.feature_columns, importance))
        else:
            return {}

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        if not self.is_trained:
            return {'error': '模型尚未训练'}

        return {
            'model_type': self.best_model_name,
            'feature_columns': self.feature_columns,
            'feature_importance': self.get_feature_importance(),
            'is_trained': self.is_trained,
            'model_path': self.model_path
        }

# 全局预测器实例
_predictor_instance = None

def get_demand_predictor() -> BikeDemandPredictor:
    """获取预测器实例（单例模式）"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = BikeDemandPredictor()
        # 尝试加载已训练的模型
        try:
            _predictor_instance.load_model()
            logger.info("预测器实例已创建并加载模型")
        except FileNotFoundError:
            logger.info("预测器实例已创建，但未找到训练好的模型")
        except Exception as e:
            logger.warning(f"加载模型时出错: {e}")

    return _predictor_instance

def predict_demand_for_station(
    station_type: int,
    temp: float,
    is_holiday: int,
    weather: int,
    weekday: int,
    date_str: str
) -> Dict[str, Any]:
    """
    为特定站点预测需求量的便捷函数

    参数:
    - station_type: 站点类型 (0-3)
    - temp: 温度
    - is_holiday: 是否节假日 (0/1)
    - weather: 天气状况
    - weekday: 星期几 (0-6, 0为周日)
    - date_str: 日期时间字符串 (格式: "2024/9/1 7:02")

    返回:
    - 预测结果字典
    """
    predictor = get_demand_predictor()

    input_data = {
        'date': date_str,
        'station_type': station_type,
        'temp': temp,
        'is_holiday': is_holiday,
        'weather': weather,
        'weekday': weekday
    }

    return predictor.predict(input_data)