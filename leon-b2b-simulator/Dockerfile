# Usamos una imagen ligera de Python
FROM python:3.9-slim

# 1. INSTALACIÓN DE DEPENDENCIAS DEL SISTEMA
# ffmpeg es esencial para el procesamiento de audio con pydub
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. PREPARAR EL DIRECTORIO DE TRABAJO
WORKDIR /app

# 3. INSTALAR LIBRERÍAS DE PYTHON
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. COPIAR TU CÓDIGO
COPY . .

# 5. CONFIGURACIÓN DE STREAMLIT PARA CLOUD RUN
# Deshabilitamos el navegador y CORS para evitar bloqueos en la URL pública
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 6. COMANDO DE ARRANQUE
# Usamos "sh -c" para que Streamlit escuche en el puerto que Cloud Run asigne
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0"]