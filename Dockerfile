# Dockerfile

# Use Debian bookworm to avoid missing/renamed packages on trixie
FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install OS deps + Chromium + Chromedriver + required libraries
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

WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Run with Gunicorn on the port Render provides
# (Render injects $PORT env var)
CMD exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
