#!/bin/bash

# 1. Ajustar el puerto de Nginx al que Cloud Run nos asigne
echo "Configuring Nginx on port ${PORT:-8080}..."
sed -i "s/listen 8080;/listen ${PORT:-8080};/g" /etc/nginx/sites-available/default

# 2. Iniciar el Backend de Audio en segundo plano con logs redirigidos a /tmp
echo "Starting Live Mode Backend on port 8000..."
python3 live_mode_backend.py > /tmp/backend.log 2>&1 &

# 3. Iniciar Streamlit y capturar su salida a /tmp
echo "Starting Streamlit App on port 8501..."
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true > /tmp/streamlit.log 2>&1 &

# 4. Iniciar Nginx en primer plano
echo "Starting Nginx Reverse Proxy in foreground..."
nginx -g 'daemon off;'
