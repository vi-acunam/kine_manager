# 1. Usamos la versión "Bookworm" (Estable) para que no cambien los nombres de paquetes
FROM python:3.11-slim-bookworm

# 2. Configuración de Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. INSTALAR DEPENDENCIAS (Nombres corregidos para Debian Bookworm)
RUN apt-get update && apt-get install -y \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# 4. CARPETA DE TRABAJO
WORKDIR /app

# 5. INSTALAR LIBRERÍAS DE PYTHON
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. COPIAR PROYECTO
COPY . .

# 7. ARCHIVOS ESTÁTICOS
RUN python manage.py collectstatic --noinput

# 8. INICIAR SERVIDOR
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT