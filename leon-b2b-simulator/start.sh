#!/bin/bash

# 1. Ajustar el puerto de Nginx al que Cloud Run nos asigne
echo "Configuring Nginx on port ${PORT:-8080}..."
sed -i "s/listen 8080;/listen ${PORT:-8080};/g" /etc/nginx/sites-available/default

# 2. Iniciar el Backend de Audio en segundo plano con logs redirigidos
echo "Starting Live Mode Backend on port 8000..."
python3 live_mode_backend.py > backend.log 2>&1 &

# 3. Iniciar Nginx
echo "Starting Nginx Reverse Proxy..."
service nginx start

# 4. Iniciar Streamlit y capturar su salida
echo "Starting Streamlit App on port 8501..."
# Usamos 0.0.0.0 para mayor compatibilidad interna del contenedor
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true > streamlit.log 2>&1 &

# 5. Mantener el script vivo y monitorear logs
echo "Monitoring logs..."
tail -f backend.log streamlit.log /var/log/nginx/error.log
