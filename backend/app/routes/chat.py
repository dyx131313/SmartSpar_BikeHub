"""
群聊功能API路由
"""
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.chat_models import *
from app.utils.database import get_db_connection
from app.utils.auth import admin_required
from app.routes import api_bp
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename


def allowed_file(filename):
    """检查文件类型是否允许"""
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

        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取用户加入的群聊
        query = """
        SELECT cg.*,
               COUNT(cgm.id) as member_count,
               MAX(cm.created_at) as last_message_time,
               cgm.role as user_role,
               cgm.is_muted,
               cgm.last_read_at,
               (SELECT COUNT(*) FROM chat_messages cm2
                WHERE cm2.group_id = cg.id
                AND cm2.created_at > COALESCE(cgm.last_read_at, '1970-01-01')
                AND cm2.sender_id != %s) as unread_count
        FROM chat_groups cg
        INNER JOIN chat_group_members cgm ON cg.id = cgm.group_id
        LEFT JOIN chat_messages cm ON cg.id = cm.group_id
        WHERE cgm.user_id = %s AND cgm.is_active = 1 AND cg.is_active = 1
        GROUP BY cg.id
        ORDER BY last_message_time DESC, cg.created_at DESC
        LIMIT %s OFFSET %s
        """

        offset = (page - 1) * page_size
        cursor.execute(query, (user_id, user_id, page_size, offset))
        groups = cursor.fetchall()

        # 获取总数
        count_query = """
        SELECT COUNT(*) as total
        FROM chat_groups cg
        INNER JOIN chat_group_members cgm ON cg.id = cgm.group_id
        WHERE cgm.user_id = %s AND cgm.is_active = 1 AND cg.is_active = 1
        """
        cursor.execute(count_query, (user_id,))
        total = cursor.fetchone()['total']

        cursor.close()
        conn.close()

        return jsonify({
            'groups': groups,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_more': offset + page_size < total
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取群聊列表失败: {str(e)}")
        return jsonify({'error': '获取群聊列表失败'}), 500


@api_bp.route("/chat/groups", methods=['POST'])
@jwt_required()
def create_chat_group():
    """创建群聊"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # 验证输入数据 - 兼容前端格式
        try:
            group_data = ChatGroupCreate(**data)
        except Exception as e:
            # 如果验证失败，尝试使用基础模型
            from app.models.chat_models import ChatGroupBase
            group_data = ChatGroupBase(**data)

        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建群聊
        query = """
        INSERT INTO chat_groups (name, description, avatar_url, group_type, max_members, created_by)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            group_data.name,
            group_data.description,
            group_data.avatar_url,
            group_data.group_type.value,
            group_data.max_members,
            user_id
        ))

        group_id = cursor.lastrowid

        # 创建者自动成为群主
        member_query = """
        INSERT INTO chat_group_members (group_id, user_id, role, is_active)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(member_query, (group_id, user_id, 'owner', 1))

        conn.commit()

        # 获取创建的群聊信息
        cursor.execute("SELECT * FROM chat_groups WHERE id = %s", (group_id,))
        group = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            'message': '群聊创建成功',
            'group': group
        }), 201

    except Exception as e:
        current_app.logger.error(f"创建群聊失败: {str(e)}")
        return jsonify({'error': '创建群聊失败'}), 500


@api_bp.route("/chat/groups/<int:group_id>", methods=['GET'])
@jwt_required()
def get_chat_group(group_id):
    """获取群聊详情"""
    try:
        user_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户是否是群成员
        check_query = """
        SELECT cgm.*, cg.group_type
        FROM chat_group_members cgm
        INNER JOIN chat_groups cg ON cgm.group_id = cg.id
        WHERE cgm.group_id = %s AND cgm.user_id = %s AND cgm.is_active = 1 AND cg.is_active = 1
        """
        cursor.execute(check_query, (group_id, user_id))
        membership = cursor.fetchone()

        if not membership:
            cursor.close()
            conn.close()
            return jsonify({'error': '您不是该群聊的成员'}), 403

        # 获取群聊信息
        group_query = """
        SELECT cg.*, COUNT(cgm2.id) as member_count
        FROM chat_groups cg
        LEFT JOIN chat_group_members cgm2 ON cg.id = cgm2.group_id AND cgm2.is_active = 1
        WHERE cg.id = %s
        GROUP BY cg.id
        """
        cursor.execute(group_query, (group_id,))
        group = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({'group': group}), 200

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

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户权限
        check_query = """
        SELECT cgm.*, cg.group_type
        FROM chat_group_members cgm
        INNER JOIN chat_groups cg ON cgm.group_id = cg.id
        WHERE cgm.group_id = %s AND cgm.user_id = %s AND cgm.is_active = 1 AND cg.is_active = 1
        """
        cursor.execute(check_query, (group_id, user_id))
        membership = cursor.fetchone()

        if not membership:
            cursor.close()
            conn.close()
            return jsonify({'error': '您不是该群聊的成员'}), 403

        # 获取群聊成员
        query = """
        SELECT cgm.*, u.username, u.full_name, u.email, u.role as user_role
        FROM chat_group_members cgm
        INNER JOIN users u ON cgm.user_id = u.id
        WHERE cgm.group_id = %s AND cgm.is_active = 1
        ORDER BY FIELD(cgm.role, 'owner', 'admin', 'member'), cgm.joined_at ASC
        LIMIT %s OFFSET %s
        """

        offset = (page - 1) * page_size
        cursor.execute(query, (group_id, page_size, offset))
        members = cursor.fetchall()

        # 获取总数
        count_query = """
        SELECT COUNT(*) as total
        FROM chat_group_members cgm
        WHERE cgm.group_id = %s AND cgm.is_active = 1
        """
        cursor.execute(count_query, (group_id,))
        total = cursor.fetchone()['total']

        cursor.close()
        conn.close()

        return jsonify({
            'members': members,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_more': offset + page_size < total
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
        user_ids = data.get('user_ids', [])

        if not user_ids:
            return jsonify({'error': '请选择要添加的用户'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户权限（只有群主和管理员可以添加成员）
        check_query = """
        SELECT cgm.*, cg.max_members
        FROM chat_group_members cgm
        INNER JOIN chat_groups cg ON cgm.group_id = cg.id
        WHERE cgm.group_id = %s AND cgm.user_id = %s AND cgm.is_active = 1 AND cg.is_active = 1
        """
        cursor.execute(check_query, (group_id, user_id))
        membership = cursor.fetchone()

        if not membership or membership['role'] not in ['owner', 'admin']:
            cursor.close()
            conn.close()
            return jsonify({'error': '您没有权限添加成员'}), 403

        # 检查当前成员数量
        current_count_query = """
        SELECT COUNT(*) as count
        FROM chat_group_members
        WHERE group_id = %s AND is_active = 1
        """
        cursor.execute(current_count_query, (group_id,))
        current_count = cursor.fetchone()['count']

        if current_count + len(user_ids) > membership['max_members']:
            cursor.close()
            conn.close()
            return jsonify({'error': f'群聊成员数量不能超过{membership["max_members"]}人'}), 400

        # 添加成员
        added_members = []
        for target_user_id in user_ids:
            # 检查用户是否已存在
            exist_query = """
            SELECT id FROM chat_group_members
            WHERE group_id = %s AND user_id = %s
            """
            cursor.execute(exist_query, (group_id, target_user_id))
            existing = cursor.fetchone()

            if existing:
                # 如果已存在但未激活，则重新激活
                update_query = """
                UPDATE chat_group_members
                SET is_active = 1, joined_at = NOW(), role = 'member'
                WHERE group_id = %s AND user_id = %s
                """
                cursor.execute(update_query, (group_id, target_user_id))
            else:
                # 新增成员
                insert_query = """
                INSERT INTO chat_group_members (group_id, user_id, role, is_active)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_query, (group_id, target_user_id, 'member', 1))

            added_members.append(target_user_id)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'message': f'成功添加{len(added_members)}名成员',
            'added_user_ids': added_members
        }), 200

    except Exception as e:
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

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户是否是群成员
        check_query = """
        SELECT cgm.*, cg.group_type
        FROM chat_group_members cgm
        INNER JOIN chat_groups cg ON cgm.group_id = cg.id
        WHERE cgm.group_id = %s AND cgm.user_id = %s AND cgm.is_active = 1 AND cg.is_active = 1
        """
        cursor.execute(check_query, (group_id, user_id))
        membership = cursor.fetchone()

        if not membership:
            cursor.close()
            conn.close()
            return jsonify({'error': '您不是该群聊的成员'}), 403

        # 构建查询条件
        where_clause = "WHERE cm.group_id = %s AND cm.is_deleted = 0"
        params = [group_id]

        if before_message_id:
            where_clause += " AND cm.id < %s"
            params.append(before_message_id)

        # 获取消息列表
        query = f"""
        SELECT cm.*, u.username, u.full_name,
               (SELECT COUNT(*) FROM chat_message_reads cmr
                WHERE cmr.message_id = cm.id AND cmr.user_id = %s) as is_read_by_me
        FROM chat_messages cm
        INNER JOIN users u ON cm.sender_id = u.id
        {where_clause}
        ORDER BY cm.created_at DESC
        LIMIT %s OFFSET %s
        """

        offset = (page - 1) * page_size
        cursor.execute(query, [user_id] + params + [page_size, offset])
        messages = cursor.fetchall()

        # 获取总数
        count_query = f"""
        SELECT COUNT(*) as total
        FROM chat_messages cm
        {where_clause}
        """
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        # 更新用户最后阅读时间
        update_read_query = """
        UPDATE chat_group_members
        SET last_read_at = NOW()
        WHERE group_id = %s AND user_id = %s
        """
        cursor.execute(update_read_query, (group_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'messages': messages,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_more': offset + page_size < total
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取群聊消息失败: {str(e)}")
        return jsonify({'error': '获取群聊消息失败'}), 500


@api_bp.route("/chat/groups/<int:group_id>/messages", methods=['POST'])
@jwt_required()
def send_group_message(group_id):
    """发送群聊消息"""
    try:
        user_id = get_jwt_identity()
        current_app.logger.info(f"收到群聊消息请求 - group_id: {group_id}, user_id: {user_id}")

        # 检查文件上传
        file_url = None
        file_name = None
        file_size = None
        message_type = MessageType.TEXT

        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 这里应该实现文件上传逻辑，保存到文件服务器或云存储
                # 暂时返回文件名作为示例
                file_url = f"/uploads/{filename}"
                file_name = filename
                file_size = len(file.read())
                file.seek(0)  # 重置文件指针

                # 根据文件类型确定消息类型
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    message_type = MessageType.IMAGE
                else:
                    message_type = MessageType.FILE

        # 获取消息内容和其他字段
        current_app.logger.info(f"请求类型: {request.content_type}")
        current_app.logger.info(f"表单数据: {dict(request.form) if request.form else 'None'}")
        current_app.logger.info(f"文件: {request.files}")

        # 总是从表单中获取内容，因为FormData应该使用request.form
        content = request.form.get('content', '')
        message_type_str = request.form.get('message_type', 'text')
        reply_to_id = request.form.get('reply_to_id', type=int)

        current_app.logger.info(f"content: '{content}', message_type: '{message_type_str}', reply_to_id: {reply_to_id}")

        if not content and not file_url:
            current_app.logger.error("消息内容为空")
            return jsonify({'error': '消息内容不能为空'}), 400

        # 转换消息类型
        message_type_str = message_type_str.upper()
        try:
            message_type = MessageType(message_type_str)
        except ValueError:
            message_type = MessageType.TEXT

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户是否是群成员
        check_query = """
        SELECT cgm.*, cg.group_type
        FROM chat_group_members cgm
        INNER JOIN chat_groups cg ON cgm.group_id = cg.id
        WHERE cgm.group_id = %s AND cgm.user_id = %s AND cgm.is_active = 1 AND cg.is_active = 1
        """
        cursor.execute(check_query, (group_id, user_id))
        membership = cursor.fetchone()

        if not membership:
            cursor.close()
            conn.close()
            return jsonify({'error': '您不是该群聊的成员'}), 403

        # 插入消息
        insert_query = """
        INSERT INTO chat_messages (group_id, sender_id, message_type, content, file_url, file_name, file_size, reply_to_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            group_id, user_id, message_type.value, content, file_url, file_name, file_size, reply_to_id
        ))

        message_id = cursor.lastrowid

        # 获取完整的消息信息
        message_query = """
        SELECT cm.*, u.username, u.full_name
        FROM chat_messages cm
        INNER JOIN users u ON cm.sender_id = u.id
        WHERE cm.id = %s
        """
        cursor.execute(message_query, (message_id,))
        message = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        # 这里应该通过WebSocket向群成员发送实时消息
        # 暂时返回消息数据
        return jsonify({
            'message': '消息发送成功',
            'data': message
        }), 201

    except Exception as e:
        current_app.logger.error(f"发送群聊消息失败: {str(e)}")
        return jsonify({'error': '发送群聊消息失败'}), 500


@api_bp.route("/chat/messages/<int:message_id>/read", methods=['POST'])
@jwt_required()
def mark_message_read(message_id):
    """标记消息为已读"""
    try:
        user_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查消息是否存在以及用户是否有权限标记
        check_query = """
        SELECT cm.*, cgm.group_id
        FROM chat_messages cm
        LEFT JOIN chat_group_members cgm ON cm.group_id = cgm.group_id
        WHERE cm.id = %s AND (cm.receiver_id = %s OR cgm.user_id = %s)
        """
        cursor.execute(check_query, (message_id, user_id, user_id))
        message = cursor.fetchone()

        if not message:
            cursor.close()
            conn.close()
            return jsonify({'error': '消息不存在或无权限'}), 404

        # 插入或更新阅读状态
        upsert_query = """
        INSERT INTO chat_message_reads (message_id, user_id, read_at)
        VALUES (%s, %s, NOW())
        ON DUPLICATE KEY UPDATE read_at = NOW()
        """
        cursor.execute(upsert_query, (message_id, user_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': '消息已标记为已读'}), 200

    except Exception as e:
        current_app.logger.error(f"标记消息已读失败: {str(e)}")
        return jsonify({'error': '标记消息已读失败'}), 500


@api_bp.route("/chat/users/search", methods=['GET'])
@jwt_required()
def search_chat_users():
    """搜索聊天用户"""
    try:
        user_id = get_jwt_identity()
        query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        # 兼容两种参数名：page_size 和 limit
        page_size = min(request.args.get('page_size', request.args.get('limit', 20, type=int), type=int), 100)
        group_id = request.args.get('group_id', type=int)  # 可选：在特定群聊内搜索

        # 如果没有查询关键词，返回所有可搜索的用户列表
        if not query:
            return get_all_searchable_users(user_id, group_id, page, page_size)

        if len(query) < 2:
            return jsonify({'error': '搜索关键词至少需要2个字符'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # 构建基础查询
        base_query = """
        SELECT DISTINCT u.id, u.username, u.full_name, u.email, u.role,
               u.is_active, u.email_verified, u.created_at
        FROM users u
        """

        params = []
        where_conditions = []

        # 基础搜索条件
        where_conditions.append("(u.username LIKE %s OR u.full_name LIKE %s OR u.email LIKE %s)")
        search_pattern = f'%{query}%'
        params.extend([search_pattern, search_pattern, search_pattern])

        # 如果指定了group_id，则只搜索该群聊内的用户
        if group_id:
            base_query += """
            INNER JOIN chat_group_members cgm ON u.id = cgm.user_id
            INNER JOIN chat_groups cg ON cgm.group_id = cg.id
            WHERE cgm.group_id = %s AND cgm.is_active = 1 AND cg.is_active = 1
            """
            params.insert(0, group_id)
        else:
            # 否则搜索所有活跃用户（创建群聊时使用）
            base_query += """
            WHERE u.id != %s AND u.is_active = 1
            """
            params.extend([user_id])

        # 添加搜索条件
        if group_id:
            where_clause = f" AND {' AND '.join(where_conditions)}"
        else:
            where_clause = f" AND {' AND '.join(where_conditions)}"

        # 完整查询
        final_query = base_query + where_clause + """
        ORDER BY
            CASE
                WHEN u.username = %s THEN 1
                WHEN u.full_name = %s THEN 2
                ELSE 3
            END,
            u.username
        LIMIT %s OFFSET %s
        """

        # 添加精确匹配参数和分页参数
        params.extend([query, query, page_size, (page - 1) * page_size])

        cursor.execute(final_query, params)
        users = cursor.fetchall()

        # 获取总数（不包含分页）
        count_query = base_query.replace("SELECT DISTINCT u.id, u.username, u.full_name, u.email, u.role,", "SELECT COUNT(DISTINCT u.id) as total,") + where_clause

        count_params = params[:-2]  # 移除分页参数
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']

        # 获取用户在共同群聊中的关系信息
        for user in users:
            # 检查用户是否已经在对方的联系人中或共同群聊
            relation_query = """
            SELECT COUNT(*) as mutual_groups,
                   (SELECT COUNT(*) FROM chat_group_members WHERE group_id IN (
                       SELECT DISTINCT cgm1.group_id
                       FROM chat_group_members cgm1
                       WHERE cgm1.user_id = %s AND cgm1.is_active = 1
                       INTERSECT
                       SELECT DISTINCT cgm2.group_id
                       FROM chat_group_members cgm2
                       WHERE cgm2.user_id = %s AND cgm2.is_active = 1
                   ) AND user_id = %s AND is_active = 1) as user_in_contact_groups
            FROM chat_groups cg
            WHERE cg.id IN (
                SELECT DISTINCT cgm1.group_id
                FROM chat_group_members cgm1
                WHERE cgm1.user_id = %s AND cgm1.is_active = 1
                INTERSECT
                SELECT DISTINCT cgm2.group_id
                FROM chat_group_members cgm2
                WHERE cgm2.user_id = %s AND cgm2.is_active = 1
            ) AND cg.is_active = 1
            """

            cursor.execute(relation_query, (user['id'], user_id, user_id, user['id'], user_id))
            relation_info = cursor.fetchone()

            user['mutual_groups'] = relation_info['mutual_groups']
            user['already_in_contact'] = relation_info['user_in_contact_groups'] > 0

        cursor.close()
        conn.close()

        return jsonify({
            'users': users,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_more': (page - 1) * page_size + len(users) < total,
            'query': query
        }), 200

    except Exception as e:
        current_app.logger.error(f"搜索聊天用户失败: {str(e)}")
        return jsonify({'error': '搜索用户失败'}), 500


@api_bp.route("/chat/search", methods=['GET'])
@jwt_required()
def search_chat():
    """搜索聊天内容"""
    try:
        user_id = get_jwt_identity()
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')  # groups, messages, users
        group_id = request.args.get('group_id', type=int)

        if not query:
            return jsonify({'error': '搜索关键词不能为空'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        result = {
            'groups': [],
            'messages': [],
            'users': [],
            'total_results': 0
        }

        # 搜索群聊
        if search_type in ['all', 'groups']:
            group_search_query = """
            SELECT DISTINCT cg.*, cgm.role as user_role
            FROM chat_groups cg
            INNER JOIN chat_group_members cgm ON cg.id = cgm.group_id
            WHERE cgm.user_id = %s AND cgm.is_active = 1 AND cg.is_active = 1
            AND (cg.name LIKE %s OR cg.description LIKE %s)
            ORDER BY cg.name
            """
            cursor.execute(group_search_query, (user_id, f'%{query}%', f'%{query}%'))
            result['groups'] = cursor.fetchall()

        # 搜索消息
        if search_type in ['all', 'messages']:
            message_search_query = """
            SELECT cm.*, u.username, u.full_name, cg.name as group_name
            FROM chat_messages cm
            INNER JOIN users u ON cm.sender_id = u.id
            INNER JOIN chat_groups cg ON cm.group_id = cg.id
            INNER JOIN chat_group_members cgm ON cg.id = cgm.group_id
            WHERE cgm.user_id = %s AND cgm.is_active = 1 AND cg.is_active = 1
            AND cm.is_deleted = 0 AND cm.content LIKE %s
            """
            params = [user_id, f'%{query}%']

            if group_id:
                message_search_query += " AND cm.group_id = %s"
                params.append(group_id)

            message_search_query += " ORDER BY cm.created_at DESC LIMIT 50"

            cursor.execute(message_search_query, params)
            result['messages'] = cursor.fetchall()

        # 搜索用户（仅在群聊内搜索）
        if search_type in ['all', 'users']:
            user_search_query = """
            SELECT DISTINCT u.id, u.username, u.full_name, u.email, u.role
            FROM users u
            INNER JOIN chat_group_members cgm1 ON u.id = cgm1.user_id
            INNER JOIN chat_group_members cgm2 ON cgm1.group_id = cgm2.group_id
            WHERE cgm2.user_id = %s AND cgm1.is_active = 1 AND cgm2.is_active = 1
            AND (u.username LIKE %s OR u.full_name LIKE %s)
            ORDER BY u.username
            LIMIT 20
            """
            cursor.execute(user_search_query, (user_id, f'%{query}%', f'%{query}%'))
            result['users'] = cursor.fetchall()

        # 计算总结果数
        result['total_results'] = len(result['groups']) + len(result['messages']) + len(result['users'])

        cursor.close()
        conn.close()

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

        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取用户的群聊统计
        stats_query = """
        SELECT
            COUNT(DISTINCT cg.id) as total_groups,
            COUNT(DISTINCT cm.id) as total_messages,
            SUM(CASE WHEN cm.created_at > COALESCE(cgm.last_read_at, '1970-01-01')
                     AND cm.sender_id != %s THEN 1 ELSE 0 END) as unread_messages,
            COUNT(DISTINCT CASE WHEN cg.is_active = 1 THEN cg.id END) as active_groups
        FROM chat_group_members cgm
        LEFT JOIN chat_groups cg ON cgm.group_id = cg.id
        LEFT JOIN chat_messages cm ON cg.id = cm.group_id AND cm.is_deleted = 0
        WHERE cgm.user_id = %s AND cgm.is_active = 1
        """

        cursor.execute(stats_query, (user_id, user_id))
        stats = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify(stats), 200

    except Exception as e:
        current_app.logger.error(f"获取聊天统计失败: {str(e)}")
        return jsonify({'error': '获取聊天统计失败'}), 500


# 管理员专用接口
@api_bp.route("/chat/admin/groups", methods=['GET'])
@admin_required
def admin_get_all_groups():
    """管理员获取所有群聊列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)

        conn = get_db_connection()
        cursor = conn.cursor()

        offset = (page - 1) * page_size

        query = """
        SELECT cg.*,
               COUNT(cgm.id) as member_count,
               u.username as creator_name,
               MAX(cm.created_at) as last_message_time
        FROM chat_groups cg
        LEFT JOIN chat_group_members cgm ON cg.id = cgm.group_id AND cgm.is_active = 1
        LEFT JOIN users u ON cg.created_by = u.id
        LEFT JOIN chat_messages cm ON cg.id = cm.group_id
        GROUP BY cg.id
        ORDER BY cg.created_at DESC
        LIMIT %s OFFSET %s
        """

        cursor.execute(query, (page_size, offset))
        groups = cursor.fetchall()

        # 获取总数
        count_query = "SELECT COUNT(*) as total FROM chat_groups"
        cursor.execute(count_query)
        total = cursor.fetchone()['total']

        cursor.close()
        conn.close()

        return jsonify({
            'groups': groups,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_more': offset + page_size < total
        }), 200

    except Exception as e:
        current_app.logger.error(f"管理员获取群聊列表失败: {str(e)}")
        return jsonify({'error': '获取群聊列表失败'}), 500


def get_all_searchable_users(user_id, group_id, page, page_size):
    """
    获取所有可搜索的用户列表（当搜索框为空时显示）
    Args:
        user_id (int): 当前用户ID
        group_id (int): 可选，指定群聊ID
        page (int): 页码
        page_size (int): 每页数量
    Returns:
        Response: JSON响应
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 如果指定了group_id，则返回该群聊的所有成员
        if group_id:
            query = """
            SELECT DISTINCT u.id, u.username, u.full_name, u.email, u.role,
                   u.is_active, u.email_verified, u.created_at,
                   1 as mutual_groups,
                   1 as already_in_contact
            FROM users u
            INNER JOIN chat_group_members cgm ON u.id = cgm.user_id
            WHERE cgm.group_id = %s AND cgm.is_active = 1 AND u.is_active = 1
            ORDER BY u.username
            LIMIT %s OFFSET %s
            """
            params = [group_id, page_size, (page - 1) * page_size]
        else:
            # 返回所有活跃用户（创建群聊时使用）
            query = """
            SELECT DISTINCT u.id, u.username, u.full_name, u.email, u.role,
                   u.is_active, u.email_verified, u.created_at,
                   0 as mutual_groups,
                   0 as already_in_contact
            FROM users u
            WHERE u.id != %s AND u.is_active = 1
            ORDER BY u.username
            LIMIT %s OFFSET %s
            """
            params = [user_id, page_size, (page - 1) * page_size]

        cursor.execute(query, params)
        users = cursor.fetchall()

        # 获取总数
        if group_id:
            count_query = """
            SELECT COUNT(DISTINCT u.id) as total
            FROM users u
            INNER JOIN chat_group_members cgm ON u.id = cgm.user_id
            WHERE cgm.group_id = %s AND cgm.is_active = 1 AND u.is_active = 1
            """
            cursor.execute(count_query, [group_id])
        else:
            count_query = """
            SELECT COUNT(DISTINCT u.id) as total
            FROM users u
            WHERE u.id != %s AND u.is_active = 1
            """
            cursor.execute(count_query, [user_id])

        total = cursor.fetchone()['total']

        cursor.close()
        conn.close()

        return jsonify({
            'users': users,
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_more': (page - 1) * page_size + len(users) < total,
            'query': ''
        }), 200

    except Exception as e:
        current_app.logger.error(f"获取可搜索用户列表失败: {str(e)}")
        return jsonify({'error': '获取用户列表失败'}), 500
