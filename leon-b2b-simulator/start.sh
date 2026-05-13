#!/bin/bash

# Cloud Run injects the PORT environment variable
NGINX_PORT=${PORT:-8080}

echo "🚀 Starting System (Port: $NGINX_PORT)..."

# 1. Update Nginx Port
sed -i "s/listen 8080;/listen $NGINX_PORT;/g" /etc/nginx/sites-available/default

# 2. Start Backend
export PYTHONPATH=/app
python3 src/api/live_mode_backend.py > /tmp/fastapi.log 2>&1 &

# 3. Start Streamlit
streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true > /tmp/streamlit.log 2>&1 &

echo "⏳ Waiting for services..."
sleep 10

# 4. Start Nginx (Foreground)
nginx -g 'daemon off;'
