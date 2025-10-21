# Usa una imagen base de Python 3.12 (compatible con PyO3)
FROM python:3.12-slim

# Establece la variable de entorno CARGO_HOME a una ruta escribible
# Esto resuelve el error "Read-only file system" de maturin/cargo
ENV CARGO_HOME="/tmp/.cargo"

# Establece la variable de entorno para forzar la compatibilidad ABI3, aunque
# ya bajamos la versión de Python, es una buena práctica de contingencia
ENV PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias del sistema operativo necesarias para compilar paquetes
# nativos (como greenlet y pydantic-core)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    # Si usas bases de datos como PostgreSQL o MySQL, añade sus librerías aquí.
    # Por ejemplo, para MySQL: default-libmysqlclient-dev
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de dependencias y el archivo Cargo.toml (si existe)
# Esto optimiza la caché de Docker.
COPY requirements.txt .

# Instala las dependencias de Python
# La opción --no-cache-dir ayuda a mantener la imagen pequeña
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación
COPY . .

# Comando para iniciar la aplicación (AJUSTAR SEGÚN TU APLICACIÓN)
# Esto asume que usas Gunicorn para ejecutar una aplicación llamada 'app'
# Asegúrate de usar la variable de entorno $PORT
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:${PORT}", "app:app"]
