#!/bin/bash

# 1. Ajustar el puerto de Nginx al que Cloud Run nos asigne
sed -i "s/listen 8080;/listen ${PORT:-8080};/g" /etc/nginx/sites-available/default

# 2. Iniciar Nginx en segundo plano
service nginx start

# 3. Iniciar el Backend de Audio en segundo plano
python3 live_mode_backend.py &

# 4. Iniciar Streamlit en primer plano (puerto interno 8501)
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
