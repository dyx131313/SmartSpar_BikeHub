CREATE DATABASE IF NOT EXISTS bikehub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE bikehub;

-- 站点信息表
CREATE TABLE IF NOT EXISTS stations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '站点名称',
    station_type VARCHAR(50) NOT NULL COMMENT '站点类型(canteen,library,teaching_building,dormitory,gate等)',
    latitude DECIMAL(10, 8) NOT NULL COMMENT '纬度',
    longitude DECIMAL(11, 8) NOT NULL COMMENT '经度',
    capacity INT NOT NULL DEFAULT 20 COMMENT '站点容量',
    description TEXT COMMENT '站点描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_station_type (station_type),
    INDEX idx_location (latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站点信息表';

-- 需求预测数据表
CREATE TABLE IF NOT EXISTS demand_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL COMMENT '时间戳',
    station_id INT NOT NULL COMMENT '站点ID',
    station_type VARCHAR(50) NOT NULL COMMENT '站点类型',
    weekday TINYINT NOT NULL COMMENT '星期几(1-7)',
    is_holiday TINYINT NOT NULL DEFAULT 0 COMMENT '是否节假日(0否,1是)',
    weather VARCHAR(20) NOT NULL COMMENT '天气状况',
    temp DECIMAL(5,2) NOT NULL COMMENT '温度(摄氏度)',
    demand INT NOT NULL COMMENT '需求数量',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_timestamp (timestamp),
    INDEX idx_station_type (station_type),
    INDEX idx_weather (weather),
    INDEX idx_weekday (weekday),
    INDEX idx_is_holiday (is_holiday)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='需求预测数据表';

-- 调度任务表
CREATE TABLE IF NOT EXISTS dispatch_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL COMMENT '任务名称',
    from_station_id INT COMMENT '起点站点ID',
    to_station_id INT COMMENT '终点站点ID',
    bike_count INT NOT NULL DEFAULT 0 COMMENT '调度单车数量',
    priority TINYINT NOT NULL DEFAULT 1 COMMENT '优先级(1-5)',
    status ENUM('pending','in_progress','completed','cancelled') NOT NULL DEFAULT 'pending' COMMENT '任务状态',
    assigned_to INT COMMENT '分配给的运维员ID',
    created_by INT NOT NULL COMMENT '创建者ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (from_station_id) REFERENCES stations(id) ON DELETE SET NULL,
    FOREIGN KEY (to_station_id) REFERENCES stations(id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_assigned_to (assigned_to)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='调度任务表';

-- 用户表 (增强版)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role ENUM('admin','dispatcher','operator','user') NOT NULL DEFAULT 'user' COMMENT '用户角色',
    full_name VARCHAR(100) COMMENT '全名',
    phone VARCHAR(20) COMMENT '电话',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    email_verified TINYINT(1) NOT NULL DEFAULT 0 COMMENT '邮箱是否验证',
    last_login TIMESTAMP NULL COMMENT '最后登录时间',
    login_count INT NOT NULL DEFAULT 0 COMMENT '登录次数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 用户会话表
CREATE TABLE IF NOT EXISTS user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    session_token VARCHAR(255) UNIQUE NOT NULL COMMENT '会话令牌',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否活跃',
    expires_at DATETIME NOT NULL COMMENT '过期时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_session_token (session_token),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户会话表';

-- 用户操作日志表
CREATE TABLE IF NOT EXISTS user_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT COMMENT '用户ID',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    resource_type VARCHAR(50) COMMENT '资源类型',
    resource_id INT COMMENT '资源ID',
    description TEXT COMMENT '操作描述',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    status ENUM('success','failure','warning') NOT NULL DEFAULT 'success' COMMENT '操作状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户操作日志表';

-- 预测结果表 
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    station_id INT NOT NULL COMMENT '站点ID',
    prediction_time DATETIME NOT NULL COMMENT '预测时间点',
    predicted_demand INT NOT NULL COMMENT '预测需求',
    predicted_bikes_needed INT NOT NULL DEFAULT 0 COMMENT '预测需要的单车数量',
    confidence_score DECIMAL(5,4) NOT NULL COMMENT '置信度分数',
    model_version VARCHAR(50) NOT NULL COMMENT '模型版本',
    prediction_type ENUM('demand','supply','dispatch') NOT NULL DEFAULT 'demand' COMMENT '预测类型',
    weather_forecast VARCHAR(20) COMMENT '天气预报',
    temp_forecast DECIMAL(5,2) COMMENT '温度预报',
    is_holiday TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否节假日',
    weekday TINYINT COMMENT '星期几(1-7)',
    actual_demand INT COMMENT '实际需求(用于模型评估)',
    accuracy_score DECIMAL(5,4) COMMENT '预测准确度',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_station_prediction (station_id, prediction_time),
    INDEX idx_prediction_time (prediction_time),
    INDEX idx_prediction_type (prediction_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预测结果表';

-- 预测模型管理表
CREATE TABLE IF NOT EXISTS prediction_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL COMMENT '模型名称',
    model_version VARCHAR(50) NOT NULL COMMENT '模型版本',
    model_type ENUM('linear_regression','random_forest','neural_network','lstm') NOT NULL COMMENT '模型类型',
    model_parameters JSON COMMENT '模型参数',
    training_data_start DATETIME COMMENT '训练数据开始时间',
    training_data_end DATETIME COMMENT '训练数据结束时间',
    accuracy_metrics JSON COMMENT '准确度指标',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_model_version (model_version),
    INDEX idx_model_type (model_type),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预测模型管理表';

-- 站点单车历史信息表
CREATE TABLE IF NOT EXISTS bike_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    station_id INT NOT NULL COMMENT '站点ID',
    timestamp DATETIME NOT NULL COMMENT '记录时间',
    available_bikes INT NOT NULL DEFAULT 0 COMMENT '可用单车数量',
    available_docks INT NOT NULL DEFAULT 0 COMMENT '可用停车位数量',
    total_bikes INT NOT NULL DEFAULT 0 COMMENT '总单车数量',
    total_docks INT NOT NULL DEFAULT 0 COMMENT '总停车位数量',
    is_station_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '站点是否激活',
    last_report_time DATETIME COMMENT '最后上报时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_station_timestamp (station_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='站点单车历史信息表';

-- 警报表
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_type ENUM('low_bikes','full_station','bike_maintenance','system_error','weather_warning','high_demand') NOT NULL COMMENT '警报类型',
    severity ENUM('low','medium','high','critical') NOT NULL COMMENT '严重程度',
    title VARCHAR(100) NOT NULL COMMENT '警报标题',
    message TEXT NOT NULL COMMENT '警报消息',
    station_id INT COMMENT '相关站点ID',
    user_id INT COMMENT '创建用户ID',
    status ENUM('active','acknowledged','resolved','dismissed') NOT NULL DEFAULT 'active' COMMENT '警报状态',
    is_resolved TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已解决',
    resolved_by INT COMMENT '解决用户ID',
    resolved_at DATETIME COMMENT '解决时间',
    resolution_notes TEXT COMMENT '解决备注',
    acknowledged_by INT COMMENT '确认用户ID',
    acknowledged_at DATETIME COMMENT '确认时间',
    alert_data JSON COMMENT '附加数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (acknowledged_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_alert_type (alert_type),
    INDEX idx_severity (severity),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='警报表';

-- 警报订阅表
CREATE TABLE IF NOT EXISTS alert_subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    alert_type ENUM('low_bikes','full_station','bike_maintenance','system_error','weather_warning','high_demand') NOT NULL COMMENT '警报类型',
    severity_min ENUM('low','medium','high','critical') NOT NULL DEFAULT 'low' COMMENT '最小严重程度',
    station_id INT COMMENT '指定站点ID(为空表示所有站点)',
    notification_method ENUM('email','sms','push','webhook') NOT NULL DEFAULT 'email' COMMENT '通知方式',
    notification_address VARCHAR(255) COMMENT '通知地址',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_alert_type (alert_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='警报订阅表';

-- 插入示例站点数据
INSERT INTO stations (name, station_type, latitude, longitude, capacity, description) VALUES
('食堂站点', 'canteen', 31.2304, 121.4737, 30, '食堂门口共享单车停放点'),
('图书馆站点', 'library', 31.2314, 121.4747, 25, '图书馆附近停车点'),
('教学楼A栋', 'teaching_building', 31.2324, 121.4757, 20, '教学楼A栋门口'),
('宿舍区1号', 'dormitory', 31.2294, 121.4727, 40, '第一宿舍区停车点'),
('南门站点', 'gate', 31.2284, 121.4717, 15, '学校南门出入口');

-- 插入示例需求数据
INSERT INTO demand_data (timestamp, station_id, station_type, weekday, is_holiday, weather, temp, demand) VALUES
('2025-07-01 08:00:00', 1, 'canteen', 2, 0, 'rain', 28.4, 14),
('2025-07-01 08:15:00', 1, 'canteen', 2, 0, 'rain', 28.6, 17),
('2025-07-01 08:30:00', 1, 'canteen', 2, 0, 'cloudy', 28.8, 19),
('2025-07-01 09:00:00', 2, 'library', 2, 0, 'cloudy', 29.0, 8),
('2025-07-01 09:15:00', 2, 'library', 2, 0, 'sunny', 29.2, 12),
('2025-07-01 12:00:00', 1, 'canteen', 2, 0, 'sunny', 31.5, 25),
('2025-07-01 12:15:00', 1, 'canteen', 2, 0, 'sunny', 31.8, 28),
('2025-07-01 18:00:00', 4, 'dormitory', 2, 0, 'cloudy', 30.2, 22),
('2025-07-01 18:15:00', 4, 'dormitory', 2, 0, 'cloudy', 30.0, 26);

-- 插入示例单车历史数据
INSERT INTO bike_history (station_id, timestamp, available_bikes, available_docks, total_bikes, total_docks) VALUES
(1, '2025-07-01 08:00:00', 15, 15, 30, 30),
(1, '2025-07-01 08:15:00', 12, 18, 30, 30),
(2, '2025-07-01 09:00:00', 18, 7, 25, 25),
(3, '2025-07-01 09:00:00', 15, 5, 20, 20),
(4, '2025-07-01 18:00:00', 25, 15, 40, 40);

-- 插入默认管理员用户 (密码: admin123)
INSERT INTO users (username, email, password_hash, role, full_name) VALUES
('admin', 'admin@bikehub.com', 'pbkdf2:sha256:260000$salt$hash', 'admin', '系统管理员');