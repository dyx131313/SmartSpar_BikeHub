**部署指南**

本文档总结了将 SmartSpar_BikeHub 部署到一台 Linux 服务器（使用 systemd + Nginx）的完整步骤，包含必要的命令、配置位置、常见问题与验证方法。

**前提条件**:
- **操作系统**: Ubuntu/Debian（其它发行版步骤类似）
- **已安装软件**: `mysql` (MariaDB/MySQL), `nginx`, `python3` (3.8+), `node`/`npm` 或 `pnpm`，`certbot`（可选）
- **仓库位置**: 假定代码位于 `/root/SmartSpar_BikeHub`

**高层步骤概览**:
- **环境准备**: 安装系统包与全局依赖（建议使用清华镜像加速 Python/Node 包）
- **后端**: 安装 Python 依赖、运行数据库迁移、初始化用户、配置并启用 systemd + Gunicorn
- **前端**: 使用清华 npm 镜像构建静态文件并部署到 Nginx 的静态目录
- **反向代理与 TLS**: 配置 Nginx 代理 `/api/` 到后端并为站点配置 HTTPS（自签名或 Let’s Encrypt）
- **运维**: 添加 `logrotate`、数据库备份脚本、监控建议

**详细步骤**

1) 准备与系统包

 - 更新包索引并安装常用工具：
```bash
sudo apt update && sudo apt install -y git curl nginx mysql-client
```

2) Python 依赖（使用清华 PyPI）

 - 建议使用独立虚拟环境；若需要全局安装可省略 venv。
```bash
cd /root/SmartSpar_BikeHub/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3) 数据库准备

 - 在 MySQL 中创建生产数据库与应用用户（示例）：
```bash
mysql -u root -p
CREATE DATABASE IF NOT EXISTS bikehub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'bikehub_user'@'127.0.0.1' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON bikehub.* TO 'bikehub_user'@'127.0.0.1';
FLUSH PRIVILEGES;
```

 - 编辑后端环境文件（示例路径：/root/SmartSpar_BikeHub/backend/.env）并填入真实值：
  - `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB` 等

4) 运行 Alembic 迁移并初始化数据

 - 先备份目标数据库，然后运行迁移：
```bash
# 备份（可选）
mysqldump -u root -p bikehub > /root/bikehub_pre_migrate.sql

# 运行迁移
cd /root/SmartSpar_BikeHub/backend
source .venv/bin/activate
FLASK_ENV=production python -m flask db upgrade

# 创建缺失测试用户（仓库内脚本）
python app/scripts/create_missing_users.py
```

5) 导入演示/初始数据（可选）

 - 仓库内有数据导入脚本（`app/scripts/import_data_*.py` & `app/utils/data_importer.py`）用于导入 station/demand/dispatch/feedback 数据
```bash
python app/scripts/import_data_demand.py
python app/scripts/import_data_task.py
python app/scripts/import_data_feedbacks.py
```

6) 前端构建（使用清华 npm 镜像）

 - 进入前端目录并构建静态文件：
```bash
cd /root/SmartSpar_BikeHub/frontend/bikehub
npm ci --registry=https://registry.npmmirror.com
npm run build

# 将生成的 dist 拷贝到 Nginx 静态目录
sudo mkdir -p /var/www/bikehub
sudo cp -r dist/* /var/www/bikehub/
sudo chown -R www-data:www-data /var/www/bikehub
```

7) Gunicorn + systemd（后端）

 - systemd 单元示例路径：/etc/systemd/system/bikehub.service
 - 示例 `ExecStart`（请根据你的 venv/路径调整）：
```ini
[Unit]
Description=SmartSpar BikeHub Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/root/SmartSpar_BikeHub/backend
ExecStart=/root/SmartSpar_BikeHub/backend/.venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 run:app
Restart=on-failure
Environment=FLASK_ENV=production
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

 - 启用并启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now bikehub
sudo systemctl status bikehub
```

8) Nginx 配置（反向代理与静态）

 - 已在仓库 `deploy/nginx/conf.d/bikehub.conf` 提供示例。可使用以下简化配置：
```nginx
server {
    listen 80;
    server_name your.domain.or.ip;
    root /var/www/bikehub;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

 - 测试并重载 Nginx：
```bash
sudo nginx -t && sudo systemctl reload nginx
```

9) TLS（两种方式）

 - 临时：生成自签名证书（适用于 IP 访问或测试）
```bash
sudo mkdir -p /etc/ssl/bikehub
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/bikehub/bikehub.key -out /etc/ssl/bikehub/bikehub.crt \
  -subj "/CN=your.ip.or.domain" -addext "subjectAltName=IP:your.ip"
```

 - 推荐（公开生产）：使用 Let’s Encrypt（需要域名 A 记录指向公网 IP）
```bash
sudo certbot --nginx -d your.domain.com
```

10) 日志轮转与备份

 - 我们已在服务器上添加 `logrotate` 配置文件：/etc/logrotate.d/bikehub
 - 数据库每日备份脚本：/usr/local/bin/bikehub_db_backup.sh（已安装到 /etc/cron.daily/ 并会把备份存到 /var/backups/bikehub）

11) 验证与常用排查命令

 - 网站访问（忽略自签名）:
```bash
curl -I -k https://YOUR_IP/
curl -sS -k https://YOUR_IP/api/health
```

 - 查看后端服务与日志：
```bash
systemctl status bikehub
journalctl -u bikehub -n 200 --no-pager
```

 - 数据库检查：
```bash
mysql -u root -p -e "USE ${MYSQL_DB}; SHOW TABLES; SELECT COUNT(*) FROM users;"
```

12) 常见问题与建议

- 如果出现 `Table 'xxx.users' doesn't exist` 错误：可能是运行时连接的数据库与已迁移数据库不一致。检查 `.env`、`SQLALCHEMY_DATABASE_URI` 并确认对齐；可将已迁移数据从 `_dev` 导入到目标数据库或调整配置指向已迁移数据库。
- 不要以 root 用户运行应用服务（建议创建 `bikehub` 或 `www-data` 运行用户并调整文件权限）。
- 生产环境建议使用 Let’s Encrypt 并定期测试备份恢复流程。

文件参考：
- Nginx 示例: [deploy/nginx/conf.d/bikehub.conf](deploy/nginx/conf.d/bikehub.conf)
- 后端 systemd 单元: [/etc/systemd/system/bikehub.service](/etc/systemd/system/bikehub.service)
- 备份脚本: [/usr/local/bin/bikehub_db_backup.sh](/usr/local/bin/bikehub_db_backup.sh)
- logrotate 配置: [/etc/logrotate.d/bikehub](/etc/logrotate.d/bikehub)

----

快速恢复步骤（如果服务报错）:

1. 检查服务状态与日志：
```bash
systemctl status bikehub
journalctl -u bikehub -n 200 --no-pager
```
2. 验证 `.env` 中数据库配置与 `SQLALCHEMY_DATABASE_URI` 一致：
```bash
grep -E "^MYSQL_" backend/.env
python - <<'PY'
from app import create_app
app = create_app()
print(app.config.get('SQLALCHEMY_DATABASE_URI'))
PY
```
3. 若缺表：将已存在的 `_dev` 库导入到目标库或在正确的目标库上运行 `flask db upgrade`（务必先备份）。

谢谢。将来需要我可以把本文件生成到仓库中的其他位置，或把某些步骤写成可执行脚本/Ansible playbook 来实现完全自动化部署。
