**一行快速说明**

本文档给出一个可复制、按步执行的部署与运维指南（适用于 Ubuntu/Debian），目标是让你能把 SmartSpar_BikeHub 部署为 systemd + nginx 托管的生产服务，并包含常见故障排查与快速修复步骤。

前提

- 假定仓库在 `/root/SmartSpar_BikeHub`。如不一致，请把下面的路径替换为你的真实路径。
- 系统已安装：`mysql`、`nginx`、`python3`（或 conda）、`node`/`npm`（或 `pnpm`）。

快速步骤概览（顺序执行）

1. 系统依赖与用户（一次性）

```bash
sudo apt update
sudo apt install -y git curl nginx mysql-client build-essential
```

2. 后端 Python 环境与依赖（使用 Conda，Python 3.13）

我们建议使用 conda 管理环境（仓库中其他脚本在运行时也使用 conda 环境 `SB_env`）。下面命令以 Miniconda 安装路径 `/root/miniconda3` 为例。

```bash
# 创建并激活 conda 环境（Python 3.13）
cd /root/SmartSpar_BikeHub/backend
/root/miniconda3/bin/conda create -n SB_env python=3.13 -y
source /root/miniconda3/bin/activate SB_env
# 更新 pip 并安装依赖
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
# 安装 gunicorn（若不在 requirements.txt 中）
pip install gunicorn
```

3. 创建数据库与用户（仅需执行一次）

把下面命令中的 `ROOT_MYSQL_PASSWORD` 与 `secure_password` 替换为实际密码：

```bash
# 交互式方式
mysql -u root -p
CREATE DATABASE IF NOT EXISTS `bikehub` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'bikehub_user'@'127.0.0.1' IDENTIFIED BY 'secure_password';
CREATE USER IF NOT EXISTS 'bikehub_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON `bikehub`.* TO 'bikehub_user'@'127.0.0.1';
GRANT ALL PRIVILEGES ON `bikehub`.* TO 'bikehub_user'@'localhost';
FLUSH PRIVILEGES;
```

4. 配置 `.env`（必须）

编辑 `/root/SmartSpar_BikeHub/backend/.env`，确保 `MYSQL_*`、`SECRET_KEY`、`JWT_SECRET_KEY` 等设置正确。我们建议在 systemd 中使用 `EnvironmentFile` 加载它：

在 `/etc/systemd/system/bikehub.service.d/override.conf` 添加：

```ini
[Service]
EnvironmentFile=/root/SmartSpar_BikeHub/backend/.env
Environment=LOG_FILE=/var/log/bikehub/app.log
```

5. 日志目录与权限（必须）

```bash
sudo mkdir -p /var/log/bikehub
sudo chown -R www-data:www-data /var/log/bikehub
sudo chmod 750 /var/log/bikehub
sudo touch /var/log/bikehub/app.log /var/log/bikehub/backup.log
sudo chown www-data:www-data /var/log/bikehub/*.log
```

6. 运行 Alembic 迁移（注意 scheduler）

说明：项目含后台 `scheduler`，启动时会尝试运行预测任务，这在迁移期间可能触发 `Table '...' doesn't exist` 错误。请在执行迁移时临时禁用 scheduler：

```bash
# 激活 conda 环境
source /root/miniconda3/bin/activate SB_env
export DISABLE_SCHEDULER=1
export FLASK_ENV=production
cd /root/SmartSpar_BikeHub/backend
python -m flask db upgrade
# 若迁移历史有问题，可先用 ORM 创建所有表，再用 alembic 标记为已应用：
# python -m flask init_db
# python -m flask db stamp head
unset DISABLE_SCHEDULER
```

7. 创建管理员（可选）

```bash
python -m flask create_admin
```

8. 导入演示/初始数据（可选）

说明：脚本 `app/scripts/import_data_*.py` 尊重当前 `FLASK_ENV`（已修改为仅在未设置时才默认 `development`），因此在导入前请显式设置目标环境：

```bash
# 激活 conda 环境并禁用 scheduler
source /root/miniconda3/bin/activate SB_env
export FLASK_ENV=production
export DISABLE_SCHEDULER=1
python app/scripts/import_data_demand.py
python app/scripts/import_data_task.py
python app/scripts/import_data_feedbacks.py
unset DISABLE_SCHEDULER
```

9. 前端构建与部署

```bash
cd /root/SmartSpar_BikeHub/frontend/bikehub
npm ci --registry=https://registry.npmmirror.com
npm run build
sudo mkdir -p /var/www/bikehub
sudo cp -r dist/* /var/www/bikehub/  # 或 cp -r build/* /var/www/bikehub/
sudo chown -R www-data:www-data /var/www/bikehub
```

10. Nginx 配置（示例）

创建 `/etc/nginx/sites-available/bikehub`：

```nginx
server {
  listen 80;
  server_name YOUR_IP_OR_DOMAIN;
  root /var/www/bikehub;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
    include proxy_params;
    proxy_set_header Host $host;
  }
}
```

启用并重载：

```bash
sudo ln -sf /etc/nginx/sites-available/bikehub /etc/nginx/sites-enabled/bikehub
sudo nginx -t && sudo systemctl reload nginx
```

11. systemd 单元（示例，使用 conda env 的 gunicorn）

注意：systemd 以非交互方式运行，不会执行 shell 的 `conda activate`。使用绝对路径指向 conda 环境中的可执行文件更可靠。

把下列内容写入 `/etc/systemd/system/bikehub.service`：

```ini
[Unit]
Description=SmartSpar BikeHub Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/root/SmartSpar_BikeHub/backend
ExecStart=/root/miniconda3/envs/SB_env/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 run:app
Restart=on-failure
Environment=FLASK_ENV=production
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=/root/SmartSpar_BikeHub/backend/.env
Environment=LOG_FILE=/var/log/bikehub/app.log

[Install]
WantedBy=multi-user.target
```

然后启用并启动：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now bikehub
sudo systemctl status bikehub
```

PyTorch 安装（conda 推荐）

如果你需要 scheduler 的 ML 功能，建议用 conda 安装 PyTorch（选择 CPU 或 CUDA 版本）：

CPU 版本示例：
```bash
/root/miniconda3/bin/conda install -n SB_env pytorch cpuonly -c pytorch -y
```

CUDA 示例（以 CUDA 12.1 为例，视你的 GPU/驱动而定）：
```bash
/root/miniconda3/bin/conda install -n SB_env pytorch pytorch-cuda=12.1 -c pytorch -c nvidia -y
```

12. TLS（推荐）

生产建议使用 Let’s Encrypt：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your.domain.com
```

13. 日志轮转与备份（已含示例脚本）

检查 `/etc/logrotate.d/bikehub` 和 `/usr/local/bin/bikehub_db_backup.sh`，按需调整目标路径与凭据。

故障排查要点

- 如果浏览器控制台或后端日志提示 `Unknown database 'bikehub'`：确认 `.env` 中 `MYSQL_DB` 和你创建的数据库一致；使用 `mysql -u root -p -e "SHOW DATABASES;"` 验证。
- 如果 `flask db upgrade` 在某个迁移文件报错（例如缺失 `users` 表），可临时：
  - 在安全环境下运行 `export DISABLE_SCHEDULER=1`，然后用 `python -m flask init_db` 创建表，再 `python -m flask db stamp head` 标记迁移已应用。
- 若 API 返回 404 或前端无法显示数据：确认你运行导入脚本时的 `FLASK_ENV`（参见第 8 步）；前端请求的 API 地址应与 Nginx 的 `proxy_pass` 对应。

常用调试命令

```bash
# 查看后端服务状态
sudo systemctl status bikehub
sudo journalctl -u bikehub -n 200 --no-pager

# 查看 nginx 状态与日志
sudo systemctl status nginx
sudo journalctl -u nginx -n 200 --no-pager

# 检查端口监听
sudo ss -ltnp | grep -E ':80|:443|:8000' || true

# 验证 API
curl -sS http://127.0.0.1:8000/api/stations | jq . | head -n 50
curl -sS http://YOUR_IP_OR_DOMAIN/api/stations | jq . | head -n 50
```

附注

- 脚本 `app/scripts/import_data_*.py` 会读取 `/root/SmartSpar_BikeHub/backend/.env`（如果存在）。运行导入前请确保 `.env` 的 `FLASK_ENV` 指向你想要导入的环境（`production` 或 `development`）。
- 若你希望我代为执行上述步骤（创建数据库、运行迁移、导入数据），请授权我在当前服务器上运行这些命令。

---

以上即为简化且可操作的部署指引；如需我将其生成成一键脚本 `deploy/deploy_one_click.sh` 的改进版或制作 Ansible playbook，我可以继续帮你实现。