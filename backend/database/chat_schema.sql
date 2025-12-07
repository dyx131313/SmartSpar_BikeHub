-- 群聊相关表结构
-- USE bikehub_dev;

-- 群聊表
CREATE TABLE IF NOT EXISTS chat_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '群聊名称',
    description TEXT COMMENT '群聊描述',
    avatar_url VARCHAR(255) COMMENT '群聊头像URL',
    group_type ENUM('public','private','system') NOT NULL DEFAULT 'public' COMMENT '群聊类型',
    max_members INT NOT NULL DEFAULT 100 COMMENT '最大成员数量',
    created_by INT NOT NULL COMMENT '创建者ID',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_group_type (group_type),
    INDEX idx_created_by (created_by),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='群聊表';

-- 群聊成员表
CREATE TABLE IF NOT EXISTS chat_group_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL COMMENT '群聊ID',
    user_id INT NOT NULL COMMENT '用户ID',
    role ENUM('owner','admin','member') NOT NULL DEFAULT 'member' COMMENT '群内角色',
    nickname VARCHAR(50) COMMENT '群内昵称',
    is_muted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否免打扰',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否在群内',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_read_at TIMESTAMP NULL COMMENT '最后阅读时间',
    FOREIGN KEY (group_id) REFERENCES chat_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_group_user (group_id, user_id),
    INDEX idx_group_id (group_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='群聊成员表';

-- 聊天消息表
CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT COMMENT '群聊ID（群聊消息）',
    sender_id INT NOT NULL COMMENT '发送者ID',
    receiver_id INT COMMENT '接收者ID（私聊消息）',
    message_type ENUM('text','image','file','system','voice') NOT NULL DEFAULT 'text' COMMENT '消息类型',
    content TEXT NOT NULL COMMENT '消息内容',
    file_url VARCHAR(255) COMMENT '文件URL',
    file_name VARCHAR(255) COMMENT '文件名',
    file_size INT COMMENT '文件大小（字节）',
    reply_to_id INT COMMENT '回复的消息ID',
    is_deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已删除',
    is_edited TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已编辑',
    edited_at TIMESTAMP NULL COMMENT '编辑时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES chat_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reply_to_id) REFERENCES chat_messages(id) ON DELETE SET NULL,
    INDEX idx_group_id (group_id),
    INDEX idx_sender_id (sender_id),
    INDEX idx_receiver_id (receiver_id),
    INDEX idx_message_type (message_type),
    INDEX idx_created_at (created_at),
    INDEX idx_reply_to_id (reply_to_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天消息表';

-- 消息阅读状态表
CREATE TABLE IF NOT EXISTS chat_message_reads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id INT NOT NULL COMMENT '消息ID',
    user_id INT NOT NULL COMMENT '用户ID',
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '阅读时间',
    FOREIGN KEY (message_id) REFERENCES chat_messages(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_message_user (message_id, user_id),
    INDEX idx_message_id (message_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息阅读状态表';

-- 用户聊天设置表
CREATE TABLE IF NOT EXISTS user_chat_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    setting_key VARCHAR(50) NOT NULL COMMENT '设置键',
    setting_value TEXT NOT NULL COMMENT '设置值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_setting (user_id, setting_key),
    INDEX idx_user_id (user_id),
    INDEX idx_setting_key (setting_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户聊天设置表';

-- 插入默认群聊
INSERT INTO chat_groups (name, description, group_type, created_by) VALUES
('系统通知群', '系统自动通知群，所有用户自动加入', 'system', 1),
('运维交流群', '运维人员交流群', 'private', 1),
('用户反馈群', '用户反馈和建议群', 'public', 1);

-- 为所有现有用户自动加入系统通知群（这里假设管理员ID为1）
-- 注意：实际部署时需要在用户注册后自动触发加入系统群的逻辑