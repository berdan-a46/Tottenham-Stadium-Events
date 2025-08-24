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

# Selenium env
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

# Copy everything into the image
WORKDIR /app
COPY . /app/

# Find and install requirements from common locations; fallback if absent
RUN set -eux; \
    REQS="requirements.txt backend/requirements.txt backend/backend/requirements.txt"; \
    FOUND=""; \
    for f in $REQS; do \
      if [ -f "/app/$f" ]; then FOUND="/app/$f"; break; fi; \
    done; \
    if [ -n "$FOUND" ]; then \
      echo "Installing Python deps from $FOUND"; \
      pip install --no-cache-dir -r "$FOUND"; \
    else \
      echo "No requirements.txt found; installing a minimal set"; \
      pip install --no-cache-dir Django gunicorn selenium django-cors-headers djangorestframework requests-html webdriver-manager; \
    fi

# Run from the folder that has manage.py
WORKDIR /app/backend

# Start Django (project package is inner "backend" -> backend/backend/wsgi.py)
CMD exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
