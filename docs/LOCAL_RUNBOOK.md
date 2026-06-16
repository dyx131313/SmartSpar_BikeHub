# SmartSpar BikeHub Local Runbook

## Frontend

```powershell
cd frontend\bikehub
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

Frontend URL:

```text
http://127.0.0.1:5173/
```

Build check:

```powershell
npm run build
```

## Backend

Use Python 3.12 on Windows:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

Backend URL:

```text
http://127.0.0.1:5000/
```

Smoke test:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/api/system/time
```

If binding `0.0.0.0:5000` is denied on Windows, use Flask's explicit local host binding:

```powershell
.\.venv\Scripts\python.exe -m flask --app run.py run --host 127.0.0.1 --port 5000 --debug
```

## MySQL Setup

The development config reads `backend\.env` and appends `_dev` in development mode. The current local verification uses a project-local MySQL instance on `127.0.0.1:3307`. With the default file, create:

```sql
CREATE DATABASE bikehub_test_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'bikehub_test_user'@'localhost' IDENTIFIED BY 'Test_1234';
GRANT ALL PRIVILEGES ON bikehub_test_dev.* TO 'bikehub_test_user'@'localhost';
FLUSH PRIVILEGES;
```

Initialize tables and users:

```powershell
cd backend
$env:FLASK_APP = "run.py"
.\.venv\Scripts\flask.exe init-db
.\.venv\Scripts\flask.exe create-admin
.\.venv\Scripts\flask.exe create-dispatcher
.\.venv\Scripts\flask.exe create-operator
```

Default test accounts:

- `admin / admin123`
- `dispatcher / dispatcher123`
- `operator / operator123`

## Optional Prediction Dependencies

The web service can start without the deep-learning stack. Running time-series prediction jobs requires installing the project's torch-compatible environment separately.

## Verification Checklist

Latest verified commands:

```powershell
cd frontend\bikehub
npm run lint
npm run build

cd ..\..\backend
.\.venv\Scripts\python.exe -m pytest
```

Expected current result:

- Frontend lint exits with code `0`; warnings remain as tracked historical cleanup items.
- Frontend production build passes; Vite may warn about large chunks.
- Backend pytest passes with `20 passed, 4 skipped`.

Prediction smoke check:

- Login with `admin / admin123`.
- Open `http://127.0.0.1:5173/demand-management`.
- Click `预测需求`.
- Confirm that `DLinear`, `TiDE`, and `TimesNet` tabs appear and DLinear prediction rows render.
