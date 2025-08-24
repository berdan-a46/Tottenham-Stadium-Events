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

# Make paths visible to Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

# --- IMPORTANT: point WORKDIR at the folder that contains manage.py ---
WORKDIR /app/backend

# Install Python deps first (path points to backend/requirements.txt)
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy ONLY the backend code into the image (keeps it smaller)
COPY backend/ /app/backend/

# If your Django project package is the inner "backend" (i.e. backend/backend/wsgi.py),
# this import path is correct from WORKDIR /app/backend:
CMD exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
