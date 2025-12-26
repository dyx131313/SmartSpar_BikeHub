#!/usr/bin/env bash
set -euo pipefail

# One-click deploy script for SmartSpar_BikeHub
# Run as root: sudo ./deploy_one_click.sh

REPO_DIR="/root/SmartSpar_BikeHub"
BACKEND_DIR="$REPO_DIR/backend"
FRONTEND_DIR="$REPO_DIR/frontend/bikehub"
VENV_DIR="$BACKEND_DIR/.venv"

if [ "$(id -u)" -ne 0 ]; then
  echo "请以 root 身份运行此脚本: sudo $0"
  exit 1
fi

echo "=== SmartSpar_BikeHub 一键部署脚本 ==="
echo "仓库位置: $REPO_DIR"

# load .env defaults if present
ENV_FILE="$BACKEND_DIR/.env"
MYSQL_HOST="127.0.0.1"
MYSQL_USER="bikehub_user"
MYSQL_PASSWORD=""
MYSQL_DB="bikehub"
if [ -f "$ENV_FILE" ]; then
  MYSQL_HOST=$(grep -E '^MYSQL_HOST=' "$ENV_FILE" | cut -d'=' -f2- || echo "$MYSQL_HOST")
  MYSQL_USER=$(grep -E '^MYSQL_USER=' "$ENV_FILE" | cut -d'=' -f2- || echo "$MYSQL_USER")
  MYSQL_PASSWORD=$(grep -E '^MYSQL_PASSWORD=' "$ENV_FILE" | cut -d'=' -f2- || echo "$MYSQL_PASSWORD")
  MYSQL_DB=$(grep -E '^MYSQL_DB=' "$ENV_FILE" | cut -d'=' -f2- || echo "$MYSQL_DB")
fi

echo "数据库 (默认来自 $ENV_FILE): host=$MYSQL_HOST db=$MYSQL_DB user=$MYSQL_USER"
read -p "如需在 MySQL 中创建数据库与用户，输入 root 密码（回车跳过）: " -s MYSQL_ROOT_PWD
echo

echo "1) 安装系统依赖（apt）"
apt update
apt install -y python3-venv python3-pip build-essential nginx nodejs npm git mysql-client || true

echo "2) 创建 Python 虚拟环境并安装依赖（使用清华 PyPI）"
mkdir -p "$BACKEND_DIR"
cd "$BACKEND_DIR"
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "3) （可选）在 MySQL 中创建数据库与用户"
if [ -n "$MYSQL_ROOT_PWD" ]; then
  echo "正在使用 root 凭据创建数据库/用户..."
  mysql -u root -p"$MYSQL_ROOT_PWD" -e "CREATE DATABASE IF NOT EXISTS \`$MYSQL_DB\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS '$MYSQL_USER'@'127.0.0.1' IDENTIFIED BY '$MYSQL_PASSWORD'; CREATE USER IF NOT EXISTS '$MYSQL_USER'@'localhost' IDENTIFIED BY '$MYSQL_PASSWORD'; GRANT ALL PRIVILEGES ON \`$MYSQL_DB\`.* TO '$MYSQL_USER'@'127.0.0.1'; GRANT ALL PRIVILEGES ON \`$MYSQL_DB\`.* TO '$MYSQL_USER'@'localhost'; FLUSH PRIVILEGES;'" || true
fi

echo "4) 运行 Alembic 迁移"
cd "$BACKEND_DIR"
export FLASK_ENV=production
export MYSQL_HOST="$MYSQL_HOST"
export MYSQL_USER="$MYSQL_USER"
export MYSQL_PASSWORD="$MYSQL_PASSWORD"
export MYSQL_DB="$MYSQL_DB"
python -m flask db upgrade || true

echo "5) 构建前端（使用清华 npm 镜像）"
if [ -d "$FRONTEND_DIR" ]; then
  cd "$FRONTEND_DIR"
  npm ci --registry=https://registry.npmmirror.com || true
  npm run build || true
  echo "复制前端构建到 /var/www/bikehub"
  mkdir -p /var/www/bikehub
  cp -r dist/* /var/www/bikehub/ 2>/dev/null || cp -r build/* /var/www/bikehub/ 2>/dev/null || true
  chown -R www-data:www-data /var/www/bikehub || true
fi

echo "6) 创建 systemd 单元（/etc/systemd/system/bikehub.service）"
[ -d /var/log/bikehub ] || mkdir -p /var/log/bikehub
chown -R www-data:www-data /var/log/bikehub || true
chmod 750 /var/log/bikehub || true
touch /var/log/bikehub/app.log /var/log/bikehub/backup.log || true
chown www-data:www-data /var/log/bikehub/*.log || true

echo "6) 创建 systemd 单元（/etc/systemd/system/bikehub.service）"
cat > /etc/systemd/system/bikehub.service <<'SERVICE'
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
Environment=LOG_FILE=/var/log/bikehub/app.log
EnvironmentFile=/root/SmartSpar_BikeHub/backend/.env

[Install]
WantedBy=multi-user.target
SERVICE

echo "7) 写入 Nginx 站点配置 (/etc/nginx/sites-available/bikehub) 并启用"
cat > /etc/nginx/sites-available/bikehub <<'NG'
server {
    listen 80;
    listen [::]:80;
    server_name _;

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

    location /static/ {
        try_files $uri $uri/ =404;
    }
}
NG

ln -sf /etc/nginx/sites-available/bikehub /etc/nginx/sites-enabled/bikehub
if [ -f /etc/nginx/sites-enabled/default ]; then rm -f /etc/nginx/sites-enabled/default; fi
nginx -t && systemctl reload nginx || true

echo "8) 日志轮转与备份脚本（若尚未存在则创建）"
if [ ! -f /etc/logrotate.d/bikehub ]; then
  cat > /etc/logrotate.d/bikehub <<'LR'
/var/log/bikehub/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root adm
    sharedscripts
    postrotate
        systemctl reload bikehub >/dev/null 2>&1 || true
    endscript
}
LR
fi

if [ ! -f /usr/local/bin/bikehub_db_backup.sh ]; then
  cat > /usr/local/bin/bikehub_db_backup.sh <<'BS'
#!/bin/bash
set -euo pipefail
ENV_FILE=/root/SmartSpar_BikeHub/backend/.env
MYSQL_HOST=127.0.0.1
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=bikehub
if [ -f "$ENV_FILE" ]; then
  MYSQL_HOST=$(grep -E '^MYSQL_HOST=' "$ENV_FILE" | cut -d'=' -f2- | tr -d '\r' || echo "$MYSQL_HOST")
  MYSQL_USER=$(grep -E '^MYSQL_USER=' "$ENV_FILE" | cut -d'=' -f2- | tr -d '\r' || echo "$MYSQL_USER")
  MYSQL_PASSWORD=$(grep -E '^MYSQL_PASSWORD=' "$ENV_FILE" | cut -d'=' -f2- | tr -d '\r' || echo "$MYSQL_PASSWORD")
  MYSQL_DB=$(grep -E '^MYSQL_DB=' "$ENV_FILE" | cut -d'=' -f2- | tr -d '\r' || echo "$MYSQL_DB")
fi
BACKUP_DIR=/var/backups/bikehub
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%F_%H%M%S")
OUT="$BACKUP_DIR/${MYSQL_DB}_$TIMESTAMP.sql.gz"
if [ -z "$MYSQL_PASSWORD" ]; then
  mysqldump -h "$MYSQL_HOST" -u "$MYSQL_USER" --single-transaction --quick --lock-tables=false "$MYSQL_DB" | gzip > "$OUT"
else
  mysqldump -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" --single-transaction --quick --lock-tables=false "$MYSQL_DB" | gzip > "$OUT"
fi
find "$BACKUP_DIR" -type f -mtime +14 -name "${MYSQL_DB}_*.sql.gz" -delete
echo "$(date '+%F %T') backup completed: $OUT" >> /var/log/bikehub/backup.log
BS
  chmod +x /usr/local/bin/bikehub_db_backup.sh
  cp /usr/local/bin/bikehub_db_backup.sh /etc/cron.daily/bikehub_db_backup
  chmod 750 /etc/cron.daily/bikehub_db_backup
fi

echo "9) 启动并启用服务"
systemctl daemon-reload || true
systemctl enable --now bikehub || true
systemctl restart bikehub || true

echo "=== 部署完成 — 验证 ==="
echo "本地 HTTP 检查："
curl -I -k http://127.0.0.1/ || true
echo "API 根响应："
curl -sS -k http://127.0.0.1/api/ || true

echo "若使用公网 IP 访问，请使用 https://YOUR_IP/（若未配置 certbot，浏览器需接受自签名证书）。"
echo "脚本结束。若需我来执行脚本请回复 'run'，或直接在服务器上以 root 运行： sudo $REPO_DIR/deploy/deploy_one_click.sh"
