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

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role ENUM('admin','dispatcher','operator','user') NOT NULL DEFAULT 'user' COMMENT '用户角色',
    full_name VARCHAR(100) COMMENT '全名',
    phone VARCHAR(20) COMMENT '电话',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    last_login TIMESTAMP NULL COMMENT '最后登录时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 预测结果表
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    station_id INT NOT NULL COMMENT '站点ID',
    prediction_time DATETIME NOT NULL COMMENT '预测时间点',
    predicted_demand INT NOT NULL COMMENT '预测需求',
    confidence_score DECIMAL(5,4) NOT NULL COMMENT '置信度分数',
    model_version VARCHAR(50) NOT NULL COMMENT '模型版本',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE CASCADE,
    INDEX idx_station_prediction (station_id, prediction_time),
    INDEX idx_prediction_time (prediction_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预测结果表';

-- 路径规划表
CREATE TABLE IF NOT EXISTS route_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(100) NOT NULL COMMENT '规划名称',
    start_station_id INT NOT NULL COMMENT '起点站点ID',
    end_station_id INT NOT NULL COMMENT '终点站点ID',

    -- 路径信息
    path_data JSON NOT NULL COMMENT '路径数据JSON',
    total_distance FLOAT NOT NULL DEFAULT 0 COMMENT '总距离(米)',
    estimated_time INT NOT NULL DEFAULT 0 COMMENT '预估时间(分钟)',
    algorithm_used VARCHAR(50) NOT NULL DEFAULT 'A*' COMMENT '使用的算法',

    -- 多点路径信息
    waypoints JSON COMMENT '途径点数据JSON',
    is_multi_point TINYINT(1) DEFAULT 0 COMMENT '是否多点路径',

    -- 业务信息
    task_id INT COMMENT '关联的调度任务ID',
    bike_capacity INT DEFAULT 20 COMMENT '单车容量',
    optimization_goal VARCHAR(20) DEFAULT 'shortest' COMMENT '优化目标(shortest/fastest/balanced)',

    -- 状态信息
    status ENUM('planned','in_progress','completed','cancelled') NOT NULL DEFAULT 'planned' COMMENT '路径状态',
    priority TINYINT DEFAULT 1 COMMENT '优先级(1-5)',

    -- 创建信息
    created_by INT NOT NULL COMMENT '创建者ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (start_station_id) REFERENCES stations(id) ON DELETE CASCADE,
    FOREIGN KEY (end_station_id) REFERENCES stations(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES dispatch_tasks(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,

    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_created_by (created_by),
    INDEX idx_task_id (task_id),
    INDEX idx_stations (start_station_id, end_station_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路径规划表';

-- 路径历史记录表
CREATE TABLE IF NOT EXISTS route_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_plan_id INT NOT NULL COMMENT '路径规划ID',

    -- 执行信息
    actual_start_time TIMESTAMP NULL COMMENT '实际开始时间',
    actual_end_time TIMESTAMP NULL COMMENT '实际结束时间',
    actual_distance FLOAT COMMENT '实际距离(米)',
    actual_time INT COMMENT '实际用时(分钟)',

    -- 执行结果
    completion_status ENUM('success','partial','failed') COMMENT '完成状态',
    bikes_transported INT DEFAULT 0 COMMENT '实际运输单车数量',
    notes TEXT COMMENT '执行备注',

    -- 评价信息
    driver_rating TINYINT COMMENT '驾驶员评分(1-5)',
    route_difficulty TINYINT COMMENT '路径难度评分(1-5)',
    traffic_conditions VARCHAR(20) COMMENT '交通状况',

    -- 反馈信息
    feedback_notes TEXT COMMENT '反馈备注',
    issues_encountered JSON COMMENT '遇到的问题',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (route_plan_id) REFERENCES route_plans(id) ON DELETE CASCADE,

    INDEX idx_route_plan_id (route_plan_id),
    INDEX idx_completion_status (completion_status),
    INDEX idx_actual_start_time (actual_start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路径历史记录表';

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

-- 插入默认管理员用户 (密码: admin123)
INSERT INTO users (username, email, password_hash, role, full_name) VALUES
('admin', 'admin@bikehub.com', 'pbkdf2:sha256:260000$salt$hash', 'admin', '系统管理员'),
('dispatcher01', 'dispather@bikehub.com', 'llll23:sha256:260000$salt$hash', 'dispatcher', '调度员');