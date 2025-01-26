# Usar una imagen base oficial de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en la imagen
WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY requirements.txt requirements.txt
COPY app.py app.py

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto para la aplicación
EXPOSE 8080

# Establecer la variable de entorno para el puerto de ejecución
ENV PORT=8080

# Comando para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
