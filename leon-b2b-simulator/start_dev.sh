#!/bin/bash

# --- CONFIGURACION DE RUTAS ---
ROOT_DIR="/home/mjgomezing/leon-b2b-simulator/leon-b2b-simulator"
VENV_PYTHON="/home/mjgomezing/leon-b2b-simulator/.venv/bin/python3"

# --- CONFIGURACION DE PROYECTO ---
export GOOGLE_CLOUD_PROJECT="b2b-agent-485013"
export GOOGLE_CLOUD_LOCATION="us-central1"

echo "🚀 Iniciando Recuperación del Sistema con Proyecto: $GOOGLE_CLOUD_PROJECT"
cd $ROOT_DIR

# 1. LIMPIEZA AGRESIVA
echo "🧹 Limpiando procesos y puertos..."
sudo pkill -9 nginx || true
sudo pkill -9 -f streamlit || true
sudo pkill -9 -f python3 || true
unset STREAMLIT_SERVER_PORT

# 2. CONFIGURAR NGINX
echo "⚙️ Configurando Nginx Proxy (Puerto 8080)..."
sudo cp $ROOT_DIR/nginx.conf /etc/nginx/sites-available/default
sudo service nginx restart

# 3. LANZAR FASTAPI (PUERTO 8000)
echo "🎙️ Lanzando Audio Backend (FastAPI) en puerto 8000..."
nohup $VENV_PYTHON live_mode_backend.py > $ROOT_DIR/fastapi.log 2>&1 &

# 4. LANZAR STREAMLIT (PUERTO 8501)
echo "🖥️ Lanzando Frontend (Streamlit) en puerto 8501..."
nohup $VENV_PYTHON -m streamlit run app.py 
    --server.port 8501 
    --server.address 0.0.0.0 
    --server.headless true 
    --browser.gatherUsageStats false 
    --server.enableCORS false 
    --server.enableXsrfProtection false > $ROOT_DIR/streamlit.log 2>&1 &

# 5. ESPERAR Y VALIDAR
echo "⏳ Esperando a que los servicios despierten (12s)..."
sleep 12

echo "--- ESTADO DE LOS SERVICIOS ---"
curl -I http://0.0.0.0:8000 > /dev/null 2>&1 && echo "✅ FastAPI: ONLINE" || echo "❌ FastAPI: OFFLINE"
curl -I http://0.0.0.0:8501 > /dev/null 2>&1 && echo "✅ Streamlit: ONLINE" || echo "❌ Streamlit: OFFLINE"
sudo ss -tulpn | grep 8080 > /dev/null 2>&1 && echo "✅ Nginx (8080): LISTENING" || echo "❌ Nginx: FAILED"

echo "=========================================================="
echo "👉 TODO LISTO. Usa el Web Preview en el PUERTO 8080."
echo "=========================================================="