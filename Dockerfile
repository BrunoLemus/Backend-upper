# 1. SOLUCIÓN PY: Usa Python 3.12 para evitar el error pyo3-ffi (3.13)
FROM python:3.12-slim

# 2. SOLUCIÓN CARGO: Establece variables de entorno escribibles
ENV CARGO_HOME="/tmp/.cargo"
ENV PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

WORKDIR /app

# 3. SOLUCIÓN APT/GREENLET: Instala dependencias del sistema operativo (en la fase de imagen)
# Esto resuelve el error de 'Read-only file system'

# Al inicio de la sección de instalación de Python
  # 4. INSTALACIÓN DE PYTHON
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. INSTALACIÓN DE PYTHON
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. EJECUCIÓN
COPY . .
# Comando de inicio de producción con Gunicorn/Uvicorn
CMD gunicorn -w 4 -b 0.0.0.0:${PORT} app:app
