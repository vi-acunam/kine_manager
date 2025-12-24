# 1. Usamos Python 3.11 sobre una base Debian (Linux estándar)
FROM python:3.11-slim

# 2. EVITAR QUE PYTHON GENERE ARCHIVOS .PYC Y SALIDA SIN BUFFER
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. INSTALAR LAS LIBRERÍAS DE SISTEMA (Pango, GDK, Fuentes)
# Esta es la parte mágica que arregla tu error
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-0b \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# 4. CREAR CARPETA DE TRABAJO
WORKDIR /app

# 5. INSTALAR LIBRERÍAS DE PYTHON (Django, WeasyPrint, etc.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. COPIAR EL RESTO DEL CÓDIGO
COPY . .

# 7. RECOLECTAR ARCHIVOS ESTÁTICOS (CSS/JS)
RUN python manage.py collectstatic --noinput

# 8. COMANDO DE INICIO (Railway inyecta la variable PORT automáticamente)
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT