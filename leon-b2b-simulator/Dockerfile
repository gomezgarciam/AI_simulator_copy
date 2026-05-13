FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    ffmpeg \
    sed \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Copy nginx config
COPY nginx.conf /etc/nginx/sites-available/default

# Grant execution permissions
RUN chmod +x start.sh

# Expose port (Cloud Run uses PORT env var, defaults to 8080)
EXPOSE 8080

CMD ["./start.sh"]
