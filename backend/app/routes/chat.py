"""
群聊功能API路由
"""
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.chat_models import (
    ChatGroup, ChatGroupMember, ChatMessage, ChatMessageRead, 
    MemberRole, MessageType, GroupType
)
from app.models import User
from app import db
from app.utils.auth import admin_required
from app.routes import api_bp
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc, and_, or_, case, distinct, literal

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api_bp.route("/chat/groups", methods=['GET'])
@jwt_required()
def get_chat_groups():
    """获取用户的群聊列表"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)

        # 子查询：计算每个群未读消息数
        # 逻辑：消息时间 > 成员最后阅读时间 且 发送者不是自己
        unread_sub = db.session.query(
            ChatMessage.group_id,
            func.count(ChatMessage.id).label('unread_count')
        ).join(ChatGroupMember, ChatMessage.group_id == ChatGroupMember.group_id)\
         .filter(
             ChatGroupMember.user_id == user_id,
             ChatGroupMember.is_active == True,
             ChatMessage.sender_id != user_id,
             ChatMessage.created_at > func.coalesce(ChatGroupMember.last_read_at, datetime(1970, 1, 1))
         ).group_by(ChatMessage.group_id).subquery()

        # 主查询：查询群组信息、成员数、最后一条消息时间等
        # 注意：这里需要左连接未读数子查询
        query = db.session.query(
            ChatGroup,
            func.count(distinct(ChatGroupMember.id)).label('member_count'),
            func.max(ChatMessage.created_at).label('last_message_time'),
            ChatGroupMember.role.label('user_role'),
            ChatGroupMember.is_muted,
            ChatGroupMember.last_read_at,
            func.coalesce(unread_sub.c.unread_count, 0).label('unread_count')
        ).join(ChatGroupMember, and_(ChatGroup.id == ChatGroupMember.group_id, ChatGroupMember.user_id == user_id))\
         .outerjoin(ChatMessage, ChatGroup.id == ChatMessage.group_id)\
         .outerjoin(unread_sub, ChatGroup.id == unread_sub.c.group_id)\
         .filter(
             ChatGroupMember.user_id == user_id,
             ChatGroupMember.is_active == True,
             ChatGroup.is_active == True
         ).group_by(
             ChatGroup.id, 
             ChatGroupMember.role, 
             ChatGroupMember.is_muted, 
             ChatGroupMember.last_read_at,
             unread_sub.c.unread_count
         ).order_by(desc('last_message_time'), desc(ChatGroup.created_at))

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        groups = []
        for item in pagination.items:
            # item 是一个 named tuple，包含查询的所有字段
            # item[0] 是 ChatGroup 对象
            group_obj = item[0]
            group_dict = group_obj.to_dict()
            group_dict.update({
                'member_count': item.member_count,
                'last_message_time': item.last_message_time.isoformat() if item.last_message_time else None,
                'user_role': item.user_role.value if hasattr(item.user_role, 'value') else item.user_role,
                'is_muted': item.is_muted,
                'last_read_at': item.last_read_at.isoformat() if item.last_read_at else None,
                'unread_count': item.unread_count
            })
            groups.append(group_dict)

        return jsonify({
            'groups': groups,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取群聊列表失败: {str(e)}")
        # db.session.rollback() # 查询通常不需要 rollback，但为了保险可以加上
        return jsonify({'error': '获取群聊列表失败'}), 500
    

@api_bp.route("/chat/groups", methods=['POST'])
@jwt_required()
def create_chat_group():
    """创建群聊"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('name'):
             return jsonify({'error': '群聊名称不能为空'}), 400

        # 创建群聊对象
        new_group = ChatGroup(
            name=data.get('name'),
            description=data.get('description'),
            avatar_url=data.get('avatar_url'),
            # group_type=data.get('group_type', GroupType.PUBLIC.value),
            # group_type=GroupType(data.get('group_type', GroupType.PUBLIC.value)),
            # group_type=GroupType[data.get('group_type', 'PUBLIC').upper()],
            group_type=data.get('group_type'),
            max_members=data.get('max_members', 100),
            created_by=user_id,
            is_active=True
        )
        
        db.session.add(new_group)
        db.session.flush() # 获取新创建的 group.id

        # 创建者自动成为群主
        owner_member = ChatGroupMember(
            group_id=new_group.id,
            user_id=user_id,
            role=MemberRole.owner,
            is_active=True,
            joined_at=datetime.now()
        )
        db.session.add(owner_member)

        db.session.commit()

        return jsonify({
            'message': '群聊创建成功',
            'group': new_group.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建群聊失败: {str(e)}")
        return jsonify({'error': '创建群聊失败'}), 500


@api_bp.route("/chat/admin/groups/<int:group_id>", methods=['DELETE'])
@admin_required
def admin_delete_chat_group(group_id):
    """删除群聊（仅管理员）"""
    try:
        # 获取群聊
        group = ChatGroup.query.get(group_id)
        if not group:
            return jsonify({'error': '群聊不存在'}), 404

        group_name = group.name

        # 删除逻辑：可以物理删除，也可以逻辑删除（设置 is_active=False）
        # 这里为了保持与原代码一致，执行物理删除关联数据
        
        # 1. 删除消息阅读状态 (需通过消息ID关联)
        # SQLAlchemy 批量删除
        subq = db.session.query(ChatMessage.id).filter(ChatMessage.group_id == group_id).subquery()
        db.session.query(ChatMessageRead).filter(ChatMessageRead.message_id.in_(subq)).delete(synchronize_session=False)

        # 2. 删除群聊消息
        db.session.query(ChatMessage).filter(ChatMessage.group_id == group_id).delete(synchronize_session=False)

        # 3. 删除群聊成员
        db.session.query(ChatGroupMember).filter(ChatGroupMember.group_id == group_id).delete(synchronize_session=False)

        # 4. 删除群聊本身
        db.session.delete(group)
        
        db.session.commit()

        return jsonify({
            'message': f'群聊"{group_name}"已被删除',
            'deleted_group_id': group_id,
            'group_name': group_name
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除群聊失败: {str(e)}")
        return jsonify({'error': '删除群聊失败'}), 500


@api_bp.route("/chat/groups/<int:group_id>", methods=['GET'])
@jwt_required()
def get_chat_group(group_id):
    """获取群聊详情"""
    try:
        user_id = get_jwt_identity()

        # 检查是否为群成员
        member = ChatGroupMember.query.filter_by(
            group_id=group_id, 
            user_id=user_id, 
            is_active=True
        ).first()

        if not member:
            return jsonify({'error': '您不是该群聊的成员'}), 403
        
        # 检查群是否活跃
        group = ChatGroup.query.filter_by(id=group_id, is_active=True).first()
        if not group:
             return jsonify({'error': '群聊不存在或已解散'}), 404

        # 获取成员总数
        member_count = ChatGroupMember.query.filter_by(group_id=group_id, is_active=True).count()

        group_data = group.to_dict()
        group_data['member_count'] = member_count

        return jsonify({'group': group_data}), 200

    except Exception as e:
        current_app.logger.error(f"获取群聊详情失败: {str(e)}")
        return jsonify({'error': '获取群聊详情失败'}), 500


@api_bp.route("/chat/groups/<int:group_id>/members", methods=['GET'])
@jwt_required()
def get_group_members(group_id):
    """获取群聊成员列表"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 50, type=int), 100)

        # 权限检查
        is_member = db.session.query(literal(True)).filter(
            db.session.query(ChatGroupMember).filter_by(
                group_id=group_id, user_id=user_id, is_active=True
            ).exists()
        ).scalar()

        if not is_member:
            return jsonify({'error': '您不是该群聊的成员'}), 403

        # 查询成员及用户信息
        # 自定义排序：owner -> admin -> member, 然后加入时间
        query = db.session.query(ChatGroupMember, User)\
            .join(User, ChatGroupMember.user_id == User.id)\
            .filter(ChatGroupMember.group_id == group_id, ChatGroupMember.is_active == True)\
            .order_by(
                case(
                    (ChatGroupMember.role == MemberRole.owner, 1),
                    (ChatGroupMember.role == MemberRole.admin, 2),
                    else_=3
                ),
                ChatGroupMember.joined_at.asc()
            )

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        members = []
        for cgm, user in pagination.items:
            member_dict = cgm.to_dict()
            member_dict.update({
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'user_role': user.role # 用户的系统角色，不是群角色
            })
            members.append(member_dict)

        return jsonify({
            'members': members,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取群聊成员失败: {str(e)}")
        return jsonify({'error': '获取群聊成员失败'}), 500


@api_bp.route("/chat/groups/<int:group_id>/members", methods=['POST'])
@jwt_required()
def add_group_members(group_id):
    """添加群聊成员"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        target_user_ids = data.get('user_ids', [])

        if not target_user_ids:
            return jsonify({'error': '请选择要添加的用户'}), 400

        # 检查权限和群最大人数
        group_info = db.session.query(ChatGroupMember, ChatGroup)\
            .join(ChatGroup, ChatGroupMember.group_id == ChatGroup.id)\
            .filter(
                ChatGroupMember.group_id == group_id,
                ChatGroupMember.user_id == user_id,
                ChatGroupMember.is_active == True,
                ChatGroup.is_active == True
            ).first()

        if not group_info:
             return jsonify({'error': '无权操作或群不存在'}), 403

        cgm_self, group = group_info
        
        # 权限判断
        if cgm_self.role not in [MemberRole.owner, MemberRole.admin]:
            return jsonify({'error': '您没有权限添加成员'}), 403   

        # 检查人数上限
        current_count = ChatGroupMember.query.filter_by(group_id=group_id, is_active=True).count()
        if current_count + len(target_user_ids) > group.max_members:
             return jsonify({'error': f'群聊成员数量不能超过{group.max_members}人'}), 400

        added_ids = []
        for target_id in target_user_ids:
            existing_member = ChatGroupMember.query.filter_by(group_id=group_id, user_id=target_id).first()
            
            if existing_member:
                if not existing_member.is_active:
                    existing_member.is_active = True
                    existing_member.joined_at = datetime.now()
                    existing_member.role = MemberRole.member
                    added_ids.append(target_id)
            else:
                new_member = ChatGroupMember(
                    group_id=group_id,
                    user_id=target_id,
                    role=MemberRole.member,
                    is_active=True
                )
                db.session.add(new_member)
                added_ids.append(target_id)

        db.session.commit()

        return jsonify({
            'message': f'成功添加{len(added_ids)}名成员',
            'added_user_ids': added_ids
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"添加群聊成员失败: {str(e)}")
        return jsonify({'error': '添加群聊成员失败'}), 500


@api_bp.route("/chat/groups/<int:group_id>/messages", methods=['GET'])
@jwt_required()
def get_group_messages(group_id):
    """获取群聊消息列表"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 50, type=int), 100)
        before_message_id = request.args.get('before_message_id', type=int)

        # 检查成员资格
        is_member = ChatGroupMember.query.filter_by(
            group_id=group_id, user_id=user_id, is_active=True
        ).first()

        if not is_member:
            return jsonify({'error': '您不是该群聊的成员'}), 403

        # 构建查询
        query = db.session.query(ChatMessage, User, 
            # 子查询：当前用户是否已读
            db.session.query(func.count(ChatMessageRead.id))
                .filter(
                    ChatMessageRead.message_id == ChatMessage.id,
                    ChatMessageRead.user_id == user_id
                ).label('is_read_by_me')
        ).join(User, ChatMessage.sender_id == User.id)\
         .filter(ChatMessage.group_id == group_id, ChatMessage.is_deleted == False)

        if before_message_id:
            query = query.filter(ChatMessage.id < before_message_id)

        # 排序和分页
        query = query.order_by(ChatMessage.created_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        messages_list = []
        for msg, user, is_read in pagination.items:
            msg_dict = msg.to_dict()
            msg_dict.update({
                'username': user.username,
                'full_name': user.full_name,
                'is_read_by_me': is_read > 0
            })
            messages_list.append(msg_dict)

        # 更新用户最后阅读时间
        ChatGroupMember.query.filter_by(group_id=group_id, user_id=user_id)\
            .update({'last_read_at': datetime.now()})
        db.session.commit()

        return jsonify({
            'messages': messages_list,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next
        }), 200

    except Exception as e:
        db.session.rollback() # 更新了last_read_at，需要rollback
        current_app.logger.error(f"获取群聊消息失败: {str(e)}")
        return jsonify({'error': '获取群聊消息失败'}), 500


@api_bp.route("/chat/groups/<int:group_id>/messages", methods=['POST'])
@jwt_required()
def send_group_message(group_id):
    """发送群聊消息"""
    try:
        user_id = get_jwt_identity()

        # 1. 检查权限
        is_member = ChatGroupMember.query.filter_by(
            group_id=group_id, user_id=user_id, is_active=True
        ).first()
        if not is_member:
             return jsonify({'error': '您不是该群聊的成员'}), 403

        # 2. 处理文件上传逻辑 (保持原样逻辑，简化存储)
        file_url = None
        file_name = None
        file_size = None
        message_type = MessageType.text

        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 实际项目请集成OSS或本地文件存储服务
                file_url = f"/uploads/{filename}"
                file_name = filename
                file_size = 0 # 需读取流长度，略
                # 简单判断类型
                ext = filename.rsplit('.', 1)[1].lower()
                if ext in ['png', 'jpg', 'jpeg', 'gif']:
                    message_type = MessageType.image
                else:
                    message_type = MessageType.file
        
        # 3. 获取表单数据
        content = request.form.get('content', '')
        req_msg_type = request.form.get('message_type')
        reply_to_id = request.form.get('reply_to_id', type=int)

        if req_msg_type:
            try:
                message_type = MessageType(req_msg_type.lower())
            except ValueError:
                pass

        if not content and not file_url:
            return jsonify({'error': '消息内容不能为空'}), 400

        # 4. 创建消息
        new_message = ChatMessage(
            group_id=group_id,
            sender_id=user_id,
            message_type=message_type,
            content=content,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
            reply_to_id=reply_to_id
        )

        db.session.add(new_message)
        db.session.commit()

        # 重新查询以获取关联信息 (如需要)
        sender = User.query.get(user_id)
        res_data = new_message.to_dict()
        res_data['username'] = sender.username
        res_data['full_name'] = sender.full_name

        return jsonify({
            'message': '消息发送成功',
            'data': res_data
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"发送群聊消息失败: {str(e)}")
        return jsonify({'error': '发送群聊消息失败'}), 500


@api_bp.route("/chat/messages/<int:message_id>/read", methods=['POST'])
@jwt_required()
def mark_message_read(message_id):
    """标记消息为已读"""
    try:
        user_id = get_jwt_identity()

        # 检查消息存在性及权限 (消息在用户所在的群里)
        # join ChatGroupMember 检查当前用户是否在群里
        message = db.session.query(ChatMessage).join(
            ChatGroupMember, ChatMessage.group_id == ChatGroupMember.group_id
        ).filter(
            ChatMessage.id == message_id,
            ChatGroupMember.user_id == user_id,
            ChatGroupMember.is_active == True
        ).first()

        if not message:
            return jsonify({'error': '消息不存在或无权限'}), 404

        # 使用 merge 或查询是否存在
        existing_read = ChatMessageRead.query.filter_by(message_id=message_id, user_id=user_id).first()
        if not existing_read:
            read_record = ChatMessageRead(message_id=message_id, user_id=user_id)
            db.session.add(read_record)
        else:
            existing_read.read_at = datetime.now()
        
        db.session.commit()
        return jsonify({'message': '消息已标记为已读'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"标记消息已读失败: {str(e)}")
        return jsonify({'error': '标记消息已读失败'}), 500


@api_bp.route("/chat/users/search", methods=['GET'])
@jwt_required()
def search_chat_users():
    """搜索聊天用户"""
    try:
        user_id = get_jwt_identity()
        query_str = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', request.args.get('limit', 20, type=int), type=int), 100)
        group_id = request.args.get('group_id', type=int)

        if not query_str:
            return get_all_searchable_users(user_id, group_id, page, page_size)

        if len(query_str) < 2:
            return jsonify({'error': '搜索关键词至少需要2个字符'}), 400

        # 构建查询
        query = db.session.query(User).filter(
            or_(
                User.username.like(f'%{query_str}%'),
                User.full_name.like(f'%{query_str}%'),
                User.email.like(f'%{query_str}%')
            ),
            User.is_active == True
        )

        if group_id:
            # 限制在特定群内搜索
            query = query.join(ChatGroupMember, User.id == ChatGroupMember.user_id)\
                .filter(ChatGroupMember.group_id == group_id, ChatGroupMember.is_active == True)
        else:
            # 排除自己
            query = query.filter(User.id != user_id)

        # 排序：完全匹配优先
        query = query.order_by(
            case(
                (User.username == query_str, 1),
                (User.full_name == query_str, 2),
                else_=3
            ),
            User.username
        )

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        user_list = []
        for u in pagination.items:
            # 计算 mutual_groups (共同群聊数)
            # 使用子查询或简单的多次查询（性能折衷）
            cgm1 = db.session.query(ChatGroupMember.group_id).filter_by(user_id=user_id, is_active=True)
            cgm2 = db.session.query(ChatGroupMember.group_id).filter_by(user_id=u.id, is_active=True)
            mutual_count = cgm1.intersect(cgm2).count()

            u_dict = {
                'id': u.id,
                'username': u.username,
                'full_name': u.full_name,
                'email': u.email,
                'role': u.role,
                'is_active': u.is_active,
                'created_at': u.created_at.isoformat() if u.created_at else None,
                'mutual_groups': mutual_count,
                'already_in_contact': mutual_count > 0 
            }
            user_list.append(u_dict)

        return jsonify({
            'users': user_list,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next,
            'query': query_str
        }), 200

    except Exception as e:
        current_app.logger.error(f"搜索聊天用户失败: {str(e)}")
        return jsonify({'error': '搜索用户失败'}), 500


@api_bp.route("/chat/search", methods=['GET'])
@jwt_required()
def search_chat():
    """搜索聊天内容（群、消息、用户）"""
    try:
        user_id = get_jwt_identity()
        q_str = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')
        group_id = request.args.get('group_id', type=int)

        if not q_str:
            return jsonify({'error': '搜索关键词不能为空'}), 400

        result = {'groups': [], 'messages': [], 'users': [], 'total_results': 0}

        # 1. 搜索群聊
        if search_type in ['all', 'groups']:
            groups = db.session.query(ChatGroup, ChatGroupMember.role)\
                .join(ChatGroupMember, ChatGroup.id == ChatGroupMember.group_id)\
                .filter(
                    ChatGroupMember.user_id == user_id,
                    ChatGroupMember.is_active == True,
                    ChatGroup.is_active == True,
                    or_(ChatGroup.name.like(f'%{q_str}%'), ChatGroup.description.like(f'%{q_str}%'))
                ).order_by(ChatGroup.name).all()
            
            result['groups'] = [dict(**g.to_dict(), user_role=r) for g, r in groups]

        # 2. 搜索消息
        if search_type in ['all', 'messages']:
            msg_query = db.session.query(ChatMessage, User.username, User.full_name, ChatGroup.name.label('group_name'))\
                .join(User, ChatMessage.sender_id == User.id)\
                .join(ChatGroup, ChatMessage.group_id == ChatGroup.id)\
                .join(ChatGroupMember, ChatGroup.id == ChatGroupMember.group_id)\
                .filter(
                    ChatGroupMember.user_id == user_id,
                    ChatGroupMember.is_active == True,
                    ChatGroup.is_active == True,
                    ChatMessage.is_deleted == False,
                    ChatMessage.content.like(f'%{q_str}%')
                )
            
            if group_id:
                msg_query = msg_query.filter(ChatMessage.group_id == group_id)

            msgs = msg_query.order_by(ChatMessage.created_at.desc()).limit(50).all()
            
            result['messages'] = []
            for m, uname, fname, gname in msgs:
                d = m.to_dict()
                d.update({'username': uname, 'full_name': fname, 'group_name': gname})
                result['messages'].append(d)

        # 3. 搜索用户 (仅搜索共同群组内的用户)
        if search_type in ['all', 'users']:
            # 逻辑：找出与我同在一个群里的用户
            subq_my_groups = db.session.query(ChatGroupMember.group_id)\
                .filter(ChatGroupMember.user_id == user_id, ChatGroupMember.is_active == True).subquery()

            users = db.session.query(distinct(User.id), User.username, User.full_name, User.email, User.role)\
                .join(ChatGroupMember, User.id == ChatGroupMember.user_id)\
                .filter(
                    ChatGroupMember.group_id.in_(subq_my_groups),
                    ChatGroupMember.is_active == True,
                    or_(User.username.like(f'%{q_str}%'), User.full_name.like(f'%{q_str}%'))
                ).order_by(User.username).limit(20).all()

            result['users'] = [
                {'id': u[0], 'username': u[1], 'full_name': u[2], 'email': u[3], 'role': u[4]} 
                for u in users
            ]

        result['total_results'] = len(result['groups']) + len(result['messages']) + len(result['users'])
        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"搜索聊天内容失败: {str(e)}")
        return jsonify({'error': '搜索聊天内容失败'}), 500


@api_bp.route("/chat/statistics", methods=['GET'])
@jwt_required()
def get_chat_statistics():
    """获取聊天统计信息"""
    try:
        user_id = get_jwt_identity()
        
        # 统计参加的群组数
        total_groups = db.session.query(ChatGroupMember)\
            .filter_by(user_id=user_id, is_active=True).count()
        
        # 统计活跃群组 (群is_active=1)
        active_groups = db.session.query(ChatGroupMember)\
            .join(ChatGroup, ChatGroupMember.group_id == ChatGroup.id)\
            .filter(ChatGroupMember.user_id == user_id, ChatGroupMember.is_active == True, ChatGroup.is_active == True)\
            .count()

        # 统计总消息数 (用户所在群的所有消息)
        # 逻辑：join 群成员表
        total_messages = db.session.query(ChatMessage)\
            .join(ChatGroupMember, ChatMessage.group_id == ChatGroupMember.group_id)\
            .filter(ChatGroupMember.user_id == user_id, ChatGroupMember.is_active == True, ChatMessage.is_deleted == False)\
            .count()

        # 统计未读消息
        # 逻辑较为复杂，需要比较 message.created_at > member.last_read_at
        unread_messages = db.session.query(ChatMessage)\
            .join(ChatGroupMember, ChatMessage.group_id == ChatGroupMember.group_id)\
            .filter(
                ChatGroupMember.user_id == user_id,
                ChatGroupMember.is_active == True,
                ChatMessage.is_deleted == False,
                ChatMessage.sender_id != user_id, # 自己发的不算未读
                ChatMessage.created_at > func.coalesce(ChatGroupMember.last_read_at, datetime(1970, 1, 1))
            ).count()

        return jsonify({
            'total_groups': total_groups,
            'active_groups': active_groups,
            'total_messages': total_messages,
            'unread_messages': unread_messages
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取聊天统计失败: {str(e)}")
        return jsonify({'error': '获取聊天统计失败'}), 500


@api_bp.route("/chat/admin/groups", methods=['GET'])
@admin_required
def admin_get_all_groups():
    """管理员获取所有群聊列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)

        query = db.session.query(
            ChatGroup,
            func.count(ChatGroupMember.id).label('member_count'),
            User.username.label('creator_name'),
            func.max(ChatMessage.created_at).label('last_message_time')
        ).outerjoin(ChatGroupMember, and_(ChatGroup.id == ChatGroupMember.group_id, ChatGroupMember.is_active == True))\
         .outerjoin(User, ChatGroup.created_by == User.id)\
         .outerjoin(ChatMessage, ChatGroup.id == ChatMessage.group_id)\
         .group_by(ChatGroup.id)\
         .order_by(ChatGroup.created_at.desc())

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        groups = []
        for g, m_count, c_name, l_time in pagination.items:
            d = g.to_dict()
            d.update({
                'member_count': m_count,
                'creator_name': c_name,
                'last_message_time': l_time.isoformat() if l_time else None
            })
            groups.append(d)

        return jsonify({
            'groups': groups,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next
        }), 200

    except Exception as e:
        current_app.logger.error(f"管理员获取群聊列表失败: {str(e)}")
        return jsonify({'error': '获取群聊列表失败'}), 500


def get_all_searchable_users(user_id, group_id, page, page_size):
    """辅助函数：获取所有可搜索用户"""
    try:
        query = db.session.query(User).filter(User.is_active == True)

        if group_id:
            query = query.join(ChatGroupMember, User.id == ChatGroupMember.user_id)\
                .filter(ChatGroupMember.group_id == group_id, ChatGroupMember.is_active == True)
        else:
            query = query.filter(User.id != user_id)

        query = query.order_by(User.username)
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        user_list = []
        for u in pagination.items:
            user_list.append({
                'id': u.id,
                'username': u.username,
                'full_name': u.full_name,
                'email': u.email,
                'role': u.role,
                'is_active': u.is_active,
                'mutual_groups': 0, 
                'already_in_contact': False
            })

        return jsonify({
            'users': user_list,
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'has_more': pagination.has_next,
            'query': ''
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取可搜索用户列表失败: {str(e)}")
        return jsonify({'error': '获取用户列表失败'}), 500