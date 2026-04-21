# Usamos una imagen ligera de Python
FROM python:3.9-slim

# 1. INSTALACIÓN DE DEPENDENCIAS DEL SISTEMA
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# 2. PREPARAR EL DIRECTORIO DE TRABAJO
WORKDIR /app

# 3. INSTALAR LIBRERÍAS DE PYTHON
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. CONFIGURACIÓN DE NGINX
COPY nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

# 5. COPIAR CÓDIGO Y SCRIPT DE ARRANQUE
COPY . .
RUN chmod +x start.sh

# 6. VARIABLES DE ENTORNO
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 7. COMANDO DE ARRANQUE
CMD ["./start.sh"]