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
    xclip \
    curl \
    ca-certificates \
    gnupg \
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
