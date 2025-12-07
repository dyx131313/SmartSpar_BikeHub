-- 添加缺失的email_verified字段到users表
USE bikehub_dev;

-- 检查字段是否已存在，如果不存在则添加
ALTER TABLE users
ADD COLUMN IF NOT EXISTS email_verified TINYINT(1) NOT NULL DEFAULT 0 COMMENT '邮箱是否验证';

-- 检查并添加缺失的索引
ALTER TABLE users
ADD INDEX IF NOT EXISTS idx_email_verified (email_verified);

-- 检查并添加缺失的login_count字段
ALTER TABLE users
ADD COLUMN IF NOT EXISTS login_count INT NOT NULL DEFAULT 0 COMMENT '登录次数';

-- 确认表结构已更新
DESCRIBE users;