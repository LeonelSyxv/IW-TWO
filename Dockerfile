# Official Python image with Node.js
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies and Node.js
RUN apt-get update && apt-get install -y \
    python3-tk \
    python3-dev \
    gcc \
    make \
    curl \
    ca-certificates \
    gnupg \
    xclip \
    libx11-6 \
    libx11-dev \
    libxtst6 \
    libxtst-dev \
    libpng-dev \
    libjpeg-dev \
    libtiff5-dev \
    libxext6 \
    libsm6 \
    libxrender1 \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxss1 \
    xdg-utils \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements first
COPY Python/requirements.txt ./Python/requirements.txt

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r Python/requirements.txt

# Copy NodeJS package files and install dependencies
COPY NodeJS/package*.json ./NodeJS/
RUN cd NodeJS && npm install && cd ..

# Copy the rest of the project
COPY . .

# Set environment variables for display (for GUI apps)
ENV DISPLAY=:0

# Start both NodeJS and Python watcher (adjust as needed)
CMD ["sh", "-c", "cd NodeJS && node index.js"]
