#!/bin/bash

# 1. Ajustar el puerto de Nginx al que Cloud Run nos asigne
echo "Configuring Nginx on port ${PORT:-8080}..."
sed -i "s/listen 8080;/listen ${PORT:-8080};/g" /etc/nginx/sites-available/default

# 2. Iniciar el Backend de Audio en segundo plano con logs a stdout
echo "Starting Live Mode Backend on port 8000..."
python3 live_mode_backend.py &

# 3. Iniciar Nginx
echo "Starting Nginx Reverse Proxy..."
service nginx start

# 4. Iniciar Streamlit en primer plano
echo "Starting Streamlit App on port 8501..."
streamlit run app.py --server.port=8501 --server.address=127.0.0.1 --server.headless=true
