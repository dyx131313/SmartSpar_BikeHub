"""
测试集成后的预测功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.demand_predictor import predict_demand_for_station, get_demand_predictor

def test_demand_prediction():
    """测试需求预测功能"""
    print("测试需求预测功能...")

    test_cases = [
        {
            'name': '早高峰工作日',
            'params': {
                'station_type': 1,
                'temp': 22.0,
                'is_holiday': 0,
                'weather': 0,
                'weekday': 1,
                'date_str': '2024/9/2 8:00'
            }
        },
        {
            'name': '晚高峰工作日',
            'params': {
                'station_type': 2,
                'temp': 25.0,
                'is_holiday': 0,
                'weather': 1,
                'weekday': 3,
                'date_str': '2024/9/4 18:30'
            }
        },
        {
            'name': '周末午后',
            'params': {
                'station_type': 0,
                'temp': 30.0,
                'is_holiday': 0,
                'weather': 0,
                'weekday': 6,
                'date_str': '2024/9/7 14:00'
            }
        },
        {
            'name': '节假日',
            'params': {
                'station_type': 3,
                'temp': 26.5,
                'is_holiday': 1,
                'weather': 2,
                'weekday': 2,
                'date_str': '2024/10/1 10:00'
            }
        }
    ]

    try:
        for test_case in test_cases:
            result = predict_demand_for_station(**test_case['params'])
            print(f"\n{test_case['name']}:")
            print(f"  预测需求量: {result['prediction']}")
            print(f"  置信度: {result['confidence']:.3f}")
            print(f"  模型类型: {result['model_type']}")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_batch_prediction():
    """测试批量预测功能"""
    print("\n\n测试批量预测功能...")

    input_data_list = [
        {
            'date': '2024/9/2 7:00',
            'station_type': 0,
            'temp': 20.0,
            'is_holiday': 0,
            'weather': 0,
            'weekday': 1
        },
        {
            'date': '2024/9/2 12:00',
            'station_type': 1,
            'temp': 28.0,
            'is_holiday': 0,
            'weather': 0,
            'weekday': 1
        },
        {
            'date': '2024/9/2 19:00',
            'station_type': 2,
            'temp': 25.0,
            'is_holiday': 0,
            'weather': 1,
            'weekday': 1
        }
    ]

    try:
        predictor = get_demand_predictor()
        results = predictor.predict_batch(input_data_list)

        print("批量预测结果:")
        for i, result in enumerate(results):
            input_data = input_data_list[i]
            print(f"  案例 {i+1}: {input_data['date']} - 预测需求量: {result['prediction']} (置信度: {result['confidence']:.3f})")

    except Exception as e:
        print(f"批量预测失败: {e}")
        import traceback
        traceback.print_exc()

def test_model_info():
    """测试获取模型信息"""
    print("\n\n测试获取模型信息...")

    try:
        predictor = get_demand_predictor()
        model_info = predictor.get_model_info()

        print("模型信息:")
        print(f"  模型类型: {model_info.get('model_type')}")
        print(f"  是否已训练: {model_info.get('is_trained')}")
        print(f"  模型路径: {model_info.get('model_path')}")

        feature_importance = model_info.get('feature_importance', {})
        if feature_importance:
            print("  特征重要性 (前10):")
            sorted_importance = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            for feature, score in sorted_importance[:10]:
                print(f"    {feature}: {score:.4f}")

    except Exception as e:
        print(f"获取模型信息失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_demand_prediction()
    test_batch_prediction()
    test_model_info()
    print("\n=== 测试完成 ===")