# Usar una imagen base oficial de Python (slim para ahorrar espacio)
FROM python:3.9-slim

# Instalar dependencias del sistema necesarias para ObsPy, matplotlib, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    libgeos-dev \
    libblas-dev \
    liblapack-dev \
    gfortran \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo en la imagen
WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY requirements.txt requirements.txt
COPY app.py app.py

# Instalar las dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto para la aplicación
EXPOSE 8080

# Establecer variable de entorno para el puerto
ENV PORT=8080

# Comando para ejecutar Gunicorn con la app Flask
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]

