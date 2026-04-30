#!/bin/bash

# Change to the script's directory to ensure relative paths work
cd "$(dirname "$0")"

# --- CONFIGURACION DE PROYECTO ---
export GOOGLE_CLOUD_PROJECT="b2b-agent-485013"
export GOOGLE_CLOUD_LOCATION="us-central1"

echo "🚀 Iniciando Recuperación del Sistema con Proyecto: $GOOGLE_CLOUD_PROJECT"

# --- INSTALACIÓN AUTOMÁTICA DE DEPENDENCIAS ---
if ! command -v nginx &> /dev/null || ! command -v ffmpeg &> /dev/null; then
    echo "📦 Instalando dependencias del sistema (Nginx y FFmpeg)..."
    sudo apt-get update
    sudo apt-get install -y nginx ffmpeg
else
    echo "✅ Nginx y FFmpeg ya están instalados."
fi
# ----------------------------------------------

# 1. LIMPIEZA DE PROCESOS (más robusta)
echo "🧹 Limpiando procesos y puertos..."

# Limpiar Nginx
sudo pkill nginx && sleep 1 || true
sudo pkill -9 nginx || true

# Limpiar Streamlit
sudo pkill -f "streamlit run app.py" && sleep 1 || true
sudo pkill -9 -f "streamlit run app.py" || true

# Limpiar FastAPI
sudo pkill -f "python3 live_mode_backend.py" && sleep 1 || true
sudo pkill -9 -f "python3 live_mode_backend.py" || true

unset STREAMLIT_SERVER_PORT

# 2. CONFIGURAR NGINX
echo "⚙️ Configurando Nginx Proxy (Puerto 8080)..."
sudo nginx -c "$(pwd)/nginx_dev.conf" & # Run Nginx in background

# 3. LANZAR FASTAPI (PUERTO 8000)
echo "🎙️ Lanzando Audio Backend (FastAPI) en puerto 8000..."
setsid python3 live_mode_backend.py > fastapi.log 2>&1 &
FASTAPI_PID=$!
echo "FastAPI PID: $FASTAPI_PID"

echo "⏳ Dando un respiro al backend (15s)..." # Aumentar el tiempo de espera
sleep 15

# Verificar si FastAPI sigue vivo
if ! ps -p $FASTAPI_PID > /dev/null
then
    echo "❌ FastAPI CRASHED unexpectedly!"
    cat fastapi.log
    exit 1
fi
echo "✅ FastAPI parece estar vivo (PID: $FASTAPI_PID)"

# 4. LANZAR STREAMLIT (PUERTO 8501)
echo "🖥️ Lanzando Frontend (Streamlit) en puerto 8501..."
setsid python3 -m streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --server.enableCORS false \
    --server.enableXsrfProtection false > streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "Streamlit PID: $STREAMLIT_PID"

echo "⏳ Esperando a que los servicios despierten (20s)..." # Aumentar el tiempo de espera
sleep 20

# Verificar si Streamlit sigue vivo
if ! ps -p $STREAMLIT_PID > /dev/null
then
    echo "❌ Streamlit CRASHED unexpectedly!"
    cat streamlit.log
    exit 1
fi
echo "✅ Streamlit parece estar vivo (PID: $STREAMLIT_PID)"


echo "--- ESTADO DE LOS SERVICIOS ---"
curl -I http://127.0.0.1:8000 > /dev/null 2>&1 && echo "✅ FastAPI: ONLINE" || echo "❌ FastAPI: OFFLINE"
curl -I http://127.0.0.1:8501 > /dev/null 2>&1 && echo "✅ Streamlit: ONLINE" || echo "❌ Streamlit: OFFLINE"
sudo ss -tulpn | grep 8080 > /dev/null 2>&1 && echo "✅ Nginx (8080): LISTENING" || echo "❌ Nginx: FAILED"

echo "=========================================================="
echo "👉 TODO LISTO. Usa el Web Preview en el PUERTO 8080."
echo "=========================================================="