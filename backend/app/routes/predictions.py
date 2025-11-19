import os
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from app import db
from app.models.prediction import Prediction
from app.models.station import Station
from app.routes import api_bp
from app.utils.permissions import require_dispatcher_or_admin
from app.services.demand_predictor import get_demand_predictor, predict_demand_for_station

@api_bp.route('/predictions', methods=['GET'])
@jwt_required()
@require_dispatcher_or_admin()
def get_predictions():
    """获取预测结果"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        station_id = request.args.get('station_id', type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        query = Prediction.query

        if station_id:
            query = query.filter(Prediction.station_id == station_id)
        if start_time:
            query = query.filter(Prediction.prediction_time >= datetime.fromisoformat(start_time))
        if end_time:
            query = query.filter(Prediction.prediction_time <= datetime.fromisoformat(end_time))

        pagination = query.order_by(Prediction.prediction_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'data': [prediction.to_dict() for prediction in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/predictions', methods=['POST'])
@jwt_required()
@require_dispatcher_or_admin()
def create_prediction():
    """创建预测结果"""
    try:
        data = request.get_json()

        # 验证站点是否存在
        station = Station.query.get(data['station_id'])
        if not station:
            return jsonify({'error': '站点不存在'}), 400

        prediction = Prediction(
            station_id=data['station_id'],
            prediction_time=datetime.fromisoformat(data['prediction_time']),
            predicted_demand=data['predicted_demand'],
            confidence_score=data['confidence_score'],
            model_version=data.get('model_version', 'v1.0')
        )

        db.session.add(prediction)
        db.session.commit()

        return jsonify({
            'message': '预测结果创建成功',
            'data': prediction.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/predictions/station/<int:station_id>', methods=['GET'])
@jwt_required()
@require_dispatcher_or_admin()
def get_station_predictions(station_id):
    """获取特定站点的预测结果"""
    try:
        # 验证站点是否存在
        station = Station.query.get_or_404(station_id)

        # 获取查询参数
        hours_ahead = request.args.get('hours_ahead', 24, type=int)
        limit = request.args.get('limit', 100, type=int)

        # 获取未来几小时的预测
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=hours_ahead)

        predictions = Prediction.query.filter(
            Prediction.station_id == station_id,
            Prediction.prediction_time >= start_time,
            Prediction.prediction_time <= end_time
        ).order_by(Prediction.prediction_time).limit(limit).all()

        return jsonify({
            'station': station.to_dict(),
            'predictions': [prediction.to_dict() for prediction in predictions],
            'total': len(predictions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/predictions/dashboard', methods=['GET'])
@jwt_required()
@require_dispatcher_or_admin()
def get_prediction_dashboard():
    """获取预测看板数据"""
    try:
        # 获取未来24小时的预测数据
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=24)

        # 获取所有站点的最新预测
        latest_predictions = db.session.query(
            Prediction.station_id,
            db.func.max(Prediction.prediction_time).label('latest_time')
        ).filter(
            Prediction.prediction_time.between(start_time, end_time)
        ).group_by(Prediction.station_id).subquery()

        predictions = db.session.query(Prediction, Station).join(
            Station, Prediction.station_id == Station.id
        ).join(
            latest_predictions,
            (Prediction.station_id == latest_predictions.c.station_id) &
            (Prediction.prediction_time == latest_predictions.c.latest_time)
        ).all()

        dashboard_data = []
        for prediction, station in predictions:
            dashboard_data.append({
                'station': station.to_dict(),
                'prediction': prediction.to_dict()
            })

        # 统计信息
        total_stations = len(dashboard_data)
        high_demand_stations = len([p for p in dashboard_data if p['prediction']['predicted_demand'] > 20])
        avg_confidence = sum(p['prediction']['confidence_score'] for p in dashboard_data) / total_stations if total_stations > 0 else 0

        return jsonify({
            'summary': {
                'total_stations': total_stations,
                'high_demand_stations': high_demand_stations,
                'avg_confidence': round(avg_confidence, 4)
            },
            'data': dashboard_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/predictions/ai', methods=['POST'])
@jwt_required()
@require_dispatcher_or_admin()
def ai_predict_demand():
    """使用AI模型进行需求预测"""
    try:
        data = request.get_json()

        # 验证必需字段
        required_fields = ['station_type', 'temp', 'is_holiday', 'weather', 'weekday', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'缺少必需字段: {field}'
                }), 400

        # 调用AI预测服务
        try:
            prediction_result = predict_demand_for_station(
                station_type=data['station_type'],
                temp=data['temp'],
                is_holiday=data['is_holiday'],
                weather=data['weather'],
                weekday=data['weekday'],
                date_str=data['date']
            )

            return jsonify({
                'success': True,
                'prediction': prediction_result,
                'input': data,
                'message': 'AI预测成功'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'AI预测失败: {str(e)}',
                'message': '预测服务暂时不可用'
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/predictions/ai/batch', methods=['POST'])
@jwt_required()
@require_dispatcher_or_admin()
def ai_predict_batch():
    """批量AI需求预测"""
    try:
        data = request.get_json()

        if 'predictions' not in data or not isinstance(data['predictions'], list):
            return jsonify({
                'error': '请求格式错误，需要predictions数组'
            }), 400

        input_data_list = data['predictions']
        predictor = get_demand_predictor()

        try:
            batch_results = predictor.predict_batch(input_data_list)

            return jsonify({
                'success': True,
                'results': batch_results,
                'total': len(batch_results),
                'successful': len(batch_results),
                'failed': 0,
                'message': '批量AI预测成功'
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'批量AI预测失败: {str(e)}',
                'message': '预测服务暂时不可用'
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/predictions/ai/model/info', methods=['GET'])
@jwt_required()
@require_dispatcher_or_admin()
def get_ai_model_info():
    """获取AI模型信息"""
    try:
        predictor = get_demand_predictor()
        model_info = predictor.get_model_info()

        return jsonify({
            'success': True,
            'model_info': model_info
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/predictions/ai/model/retrain', methods=['POST'])
@jwt_required()
@require_dispatcher_or_admin()
def retrain_ai_model():
    """重新训练AI模型"""
    try:
        predictor = get_demand_predictor()

        # 检查训练数据文件是否存在
        train_data_path = 'train.csv'
        if not os.path.exists(train_data_path):
            return jsonify({
                'success': False,
                'error': '训练数据文件不存在',
                'message': f'请确保 {train_data_path} 文件存在'
            }), 400

        # 重新训练模型
        training_results = predictor.train(train_data_path)

        return jsonify({
            'success': True,
            'message': 'AI模型重新训练完成',
            'training_results': training_results,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'重新训练失败: {str(e)}',
            'message': '模型重新训练过程中出现错误'
        }), 500