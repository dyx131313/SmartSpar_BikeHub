#!/usr/bin/env python3
"""
生成并导入用户反馈数据的脚本
"""

import sys
import os
from dotenv import load_dotenv 
from datetime import datetime, timedelta
import random

# 0. 先把 backend/.env 加载进来
current_file = os.path.abspath(__file__)
backend_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))  # scripts -> app -> backend
dotenv_path = os.path.join(backend_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# 1. 强制开发环境，避开 ProductionConfig 检查
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_CONFIG'] = 'development'

# 2. 再把 backend/ 加入路径
sys.path.insert(0, backend_root)

from app import create_app, db
from app.models.feedback import Feedback
from app.models.user import User

def generate_feedback_data(n=10):
    """生成用户反馈数据"""
    
    # 反馈类别
    categories = ['user_feedback', 'dispatcher_issue']
    
    # 反馈状态
    statuses = ['pending', 'processing', 'resolved', 'closed']
    
    # 反馈标题模板
    feedback_titles = [
        "车辆调度问题反馈",
        "站点车辆不足",
        "APP使用体验不佳",
        "车辆损坏报告",
        "调度员服务态度问题",
        "建议增加新站点",
        "系统响应速度慢",
        "车辆定位不准确",
        "计费异常问题",
        "用户界面优化建议",
        "车辆调度不及时",
        "车辆卫生状况差",
        "还车困难问题",
        "APP闪退问题",
        "优惠券使用异常"
    ]
    
    # 反馈内容模板
    feedback_contents = [
        "在高峰时段，站点车辆严重不足，希望增加车辆投放。",
        "调度员服务态度很好，点赞！",
        "APP界面设计很美观，但加载速度有点慢。",
        "今天发现站点有车辆损坏，建议及时维修。",
        "系统调度算法需要优化，经常出现调度不及时的情况。",
        "希望能在学校图书馆附近增加一个新站点。",
        "车辆定位经常漂移，导致找车困难。",
        "昨天还车时系统显示失败，但车辆已经锁上，希望能解决这个问题。",
        "调度员响应很及时，解决问题效率高。",
        "建议增加夜间调度服务。",
        "APP闪退问题严重，影响使用体验。",
        "车辆卫生状况需要改善，有的车辆比较脏。",
        "还车站点经常满位，导致还车困难。",
        "优惠券使用有时会失效，希望能修复。",
        "系统稳定性需要提升，偶尔会出现卡顿。"
    ]
    
    # 解决说明模板
    resolution_notes = [
        "问题已解决，感谢您的反馈。",
        "已联系相关调度员进行培训改进。",
        "系统已优化，问题已修复。",
        "已安排维修人员处理损坏车辆。",
        "已增加车辆投放，问题已解决。",
        "新站点规划中，感谢您的建议。",
        "定位问题已修复，现在更准确了。",
        "还车系统已优化，问题已解决。",
        "已对调度员进行表扬。",
        "夜间调度服务正在筹备中。",
        "APP闪退问题已修复，请更新到最新版本。",
        "已加强车辆清洁管理。",
        "已优化还车站点容量显示。",
        "优惠券系统已修复。",
        "系统稳定性已提升。"
    ]
    
    feedbacks = []
    
    # 首先获取用户ID列表
    app = create_app()
    with app.app_context():
        users = User.query.all()
        if not users:
            print("错误：数据库中没有用户，请先创建用户")
            return []
        
        user_ids = [user.id for user in users]
        
        # 获取可能的解决者（管理员或调度员）
        resolvers = User.query.filter(User.role.in_(['admin', 'dispatcher'])).all()
        resolver_ids = [user.id for user in resolvers]
        
        for i in range(1, n + 1):
            # 随机选择用户
            user_id = random.choice(user_ids)
            
            # 随机选择类别
            category = random.choice(categories)
            
            # 随机生成时间（最近30天内）
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # 随机决定是否已解决
            is_resolved = random.random() > 0.3  # 70%的概率已解决
            
            if is_resolved:
                status = random.choice(['resolved', 'closed'])
                resolved_by = random.choice(resolver_ids) if resolver_ids else None
                resolved_at = created_at + timedelta(hours=random.randint(1, 72))
                resolution_note = random.choice(resolution_notes)
                updated_at = resolved_at
            else:
                status = random.choice(['pending', 'processing'])
                resolved_by = None
                resolved_at = None
                resolution_note = None
                updated_at = created_at + timedelta(hours=random.randint(1, 24))
            
            feedback = {
                'id': i,
                'user_id': user_id,
                'category': category,
                'title': random.choice(feedback_titles),
                'content': random.choice(feedback_contents),
                'status': status,
                'created_at': created_at.isoformat(),
                'updated_at': updated_at.isoformat(),
                'resolution_notes': resolution_note,
                'resolved_by': resolved_by,
                'resolved_at': resolved_at.isoformat() if resolved_at else None
            }
            
            feedbacks.append(feedback)
    
    return feedbacks

def import_feedbacks():
    """导入用户反馈数据"""
    print("正在初始化应用...")
    app = create_app()
    
    with app.app_context():
        # 检查用户表是否为空
        user_count = User.query.count()
        if user_count == 0:
            print("错误：数据库中没有用户，请先创建用户")
            return False
        
        print(f"数据库中有 {user_count} 个用户")
        
        # 生成反馈数据
        feedbacks = generate_feedback_data(10)
        
        if not feedbacks:
            return False
        
        print(f"生成了 {len(feedbacks)} 条用户反馈数据")
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for idx, feedback_data in enumerate(feedbacks, 1):
            try:
                # 检查是否已存在相同ID的反馈
                existing_feedback = Feedback.query.get(feedback_data.get('id'))
                
                if existing_feedback:
                    print(f"反馈 {feedback_data.get('id')} 已存在，跳过")
                    skipped_count += 1
                    continue
                
                # 检查用户是否存在
                user_id = feedback_data.get('user_id')
                user = User.query.get(user_id)
                if not user:
                    print(f"警告：用户ID {user_id} 不存在，跳过此反馈")
                    skipped_count += 1
                    continue
                
                # 检查解决者是否存在（如果有）
                resolved_by = feedback_data.get('resolved_by')
                if resolved_by:
                    resolver = User.query.get(resolved_by)
                    if not resolver:
                        print(f"警告：解决者ID {resolved_by} 不存在，设为None")
                        feedback_data['resolved_by'] = None
                
                # 转换时间字符串为datetime对象
                for time_field in ['created_at', 'updated_at', 'resolved_at']:
                    if feedback_data.get(time_field):
                        try:
                            feedback_data[time_field] = datetime.fromisoformat(
                                feedback_data[time_field].replace('Z', '+00:00')
                            )
                        except:
                            # 如果转换失败，使用当前时间
                            feedback_data[time_field] = datetime.now()
                
                # 创建反馈对象
                feedback = Feedback(
                    id=feedback_data.get('id'),
                    user_id=feedback_data.get('user_id'),
                    category=feedback_data.get('category'),
                    title=feedback_data.get('title'),
                    content=feedback_data.get('content'),
                    status=feedback_data.get('status'),
                    created_at=feedback_data.get('created_at'),
                    updated_at=feedback_data.get('updated_at'),
                    resolution_notes=feedback_data.get('resolution_notes'),
                    resolved_by=feedback_data.get('resolved_by'),
                    resolved_at=feedback_data.get('resolved_at')
                )
                
                db.session.add(feedback)
                imported_count += 1
                
                print(f"已添加反馈: {feedback_data.get('title')} (用户ID: {user_id})")
                
            except Exception as e:
                errors.append(f"反馈 {idx} 导入失败: {str(e)}")
                skipped_count += 1
                print(f"错误：导入反馈 {idx} 时出错: {e}")
        
        try:
            db.session.commit()
            print(f"\n✅ 成功导入 {imported_count} 条用户反馈")
            
            if skipped_count > 0:
                print(f"跳过 {skipped_count} 条反馈")
            
            if errors:
                print(f"错误信息（前5条）:")
                for error in errors[:5]:
                    print(f"  - {error}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 提交到数据库失败: {e}")
            return False

def print_feedback_summary():
    """打印反馈数据摘要"""
    app = create_app()
    with app.app_context():
        # 统计反馈数据
        total_feedbacks = Feedback.query.count()
        feedbacks_by_category = db.session.query(
            Feedback.category, db.func.count(Feedback.id)
        ).group_by(Feedback.category).all()
        
        feedbacks_by_status = db.session.query(
            Feedback.status, db.func.count(Feedback.id)
        ).group_by(Feedback.status).all()
        
        print("\n" + "="*50)
        print("用户反馈数据摘要")
        print("="*50)
        print(f"总反馈数量: {total_feedbacks}")
        
        print("\n按类别统计:")
        for category, count in feedbacks_by_category:
            print(f"  {category}: {count} 条")
        
        print("\n按状态统计:")
        for status, count in feedbacks_by_status:
            print(f"  {status}: {count} 条")
        
        # 显示最新5条反馈
        latest_feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).limit(5).all()
        print("\n最新5条反馈:")
        for fb in latest_feedbacks:
            print(f"  [{fb.created_at.strftime('%Y-%m-%d %H:%M')}] {fb.title} ({fb.status})")

if __name__ == "__main__":
    try:
        print("="*50)
        print("开始导入用户反馈数据")
        print("="*50)
        
        success = import_feedbacks()
        
        if success:
            print_feedback_summary()
            print("\n✅ 用户反馈数据导入完成！")
        else:
            print("\n❌ 用户反馈数据导入失败！")
        
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 导入过程中发生错误: {e}")
        import traceback
        traceback.print_exc()