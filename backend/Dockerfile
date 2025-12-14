FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend/ /app/

# Create a non-root user (optional)
RUN useradd -m bikehub
RUN chown -R bikehub:bikehub /app
USER bikehub

# Use gunicorn to serve the app. `run:app` should expose the Flask app object.
CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app", "--workers", "3", "--timeout", "120"]
