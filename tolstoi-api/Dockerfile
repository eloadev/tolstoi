# Use the latest Ubuntu image as base
FROM ubuntu:latest

# Set the author label
LABEL authors="eloam"

# Set the working directory to /app
WORKDIR /app/

# Copy all files from the current directory to /app in the container
COPY . /app/

# Install essential packages and dependencies
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-dev \
    python3-pip \
    build-essential swig libpulse-dev \
    ffmpeg \
    curl git tmux \
    tesseract-ocr \
    xvfb \
    redis-server \
    gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcairo2-dev \
    libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 \
    libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 \
    libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 \
    libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxext6 libxfixes3 libxi6 libsm6 libxrandr2 \
    libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation \
    libappindicator1 libnss3 lsb-release xdg-utils wget

# Clean up after package installations
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Customize tmux settings
RUN echo "set -g default-terminal \"screen-256color\"" >> ~/.tmux.conf

# Install Oh My Bash
RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"

# Upgrade pip and install project requirements
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
