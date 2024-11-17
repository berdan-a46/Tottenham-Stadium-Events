# Use the official Python image as the base
FROM python:3.10-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common apt-transport-https \
    wget gnupg unzip curl libnss3 libgconf-2-4 libxi6 libxrandr2 \
    libxss1 libxcomposite1 libasound2 libpangocairo-1.0-0 libatk1.0-0 \
    libgtk-3-0 libcups2

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable --no-install-recommends && \
    apt-get clean

# Install Chromedriver
RUN CHROMEDRIVER_VERSION=`curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm chromedriver_linux64.zip

# Set environment variables for Chrome and Chromedriver
ENV GOOGLE_CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Set the working directory
WORKDIR /app/backend

# Copy application code into the container
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the application port (Django typically runs on port 8000)
EXPOSE 8000

# Start the Django application
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "1200000"]
