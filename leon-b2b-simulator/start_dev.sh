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

# 1. LIMPIEZA AGRESIVA DE PUERTOS
echo "🧹 Limpiando procesos en los puertos 8000, 8080 y 8501..."

kill_port() {
    local port=$1
    if command -v lsof &> /dev/null; then
        local pids=$(sudo lsof -t -i:$port)
        if [ -n "$pids" ]; then
            echo "   -> Matando procesos en puerto $port: $pids"
            sudo kill -9 $pids 2>/dev/null || true
        fi
    else
        # Fallback if lsof is not installed
        sudo fuser -k $port/tcp 2>/dev/null || true
    fi
}

kill_port 8000
kill_port 8080
kill_port 8501

sudo pkill -f "nginx" || true
sudo pkill -f "streamlit" || true
sudo pkill -f "uvicorn" || true
sudo pkill -9 -f "live_mode_backend.py" || true

# 2. CONFIGURAR NGINX
echo "⚙️ Configurando Nginx Proxy (Puerto 8080)..."
sudo nginx -c "$(pwd)/nginx_dev.conf" &

# 3. LANZAR FASTAPI (PUERTO 8000)
echo "🎙️ Lanzando Audio Backend (FastAPI) en puerto 8000..."
export PYTHONPATH=$(pwd)
python3 src/api/live_mode_backend.py > fastapi.log 2>&1 &
FASTAPI_PID=$!

echo "⏳ Esperando al backend (10s)..."
sleep 10

# 4. LANZAR STREAMLIT (PUERTO 8501)
echo "🖥️ Lanzando Frontend (Streamlit) en puerto 8501..."
# Añadimos flags de seguridad para entorno de Cloud Shell
python3 -m streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --server.enableCORS false \
    --server.enableXsrfProtection false > streamlit.log 2>&1 &
STREAMLIT_PID=$!

echo "⏳ Finalizando arranque (5s)..."
sleep 5

echo "--- ESTADO DE LOS SERVICIOS ---"
if ps -p $FASTAPI_PID > /dev/null; then
    echo "✅ FastAPI: ONLINE"
else
    echo "❌ FastAPI: FAILED"
    cat fastapi.log
fi

if ps -p $STREAMLIT_PID > /dev/null; then
    echo "✅ Streamlit: ONLINE"
else
    echo "❌ Streamlit: FAILED"
    cat streamlit.log
fi

echo "=========================================================="
echo "👉 APP LISTA. Usa el Web Preview en el PUERTO 8080."
echo "=========================================================="
