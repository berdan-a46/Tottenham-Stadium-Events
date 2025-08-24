# Dockerfile
FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# OS deps + Chromium + Chromedriver for Selenium
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates unzip gnupg wget \
    chromium chromium-driver \
    libnss3 libxi6 libxrandr2 libxss1 libxcomposite1 libasound2 \
    libatk1.0-0 libatk-bridge2.0-0 libpangocairo-1.0-0 libgtk-3-0 libcups2 \
    fonts-liberation libdrm2 libxkbcommon0 libgbm1 libwayland-client0 libxshmfence1 \
 && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

# Work where manage.py lives
WORKDIR /app/backend

# 👇 Copy the backend first so the file definitely exists in the image
COPY backend/ /app/backend/

# 👇 Install from the file inside backend (adjust name if different)
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Start Gunicorn; inner project package is "backend" (backend/backend/wsgi.py)
CMD exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
