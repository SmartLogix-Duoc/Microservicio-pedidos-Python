# 1. Usamos una imagen oficial de Python ligera
FROM python:3.12-slim

# 2. Evitamos que Python genere archivos .pyc y forzamos a que la consola escupa los logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiamos el archivo de dependencias primero (para aprovechar el caché de Docker)
COPY requirements.txt /app/

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 5. Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos todo el resto del código de tu proyecto al contenedor
COPY . /app/

# 7. Le avisamos a Docker que este contenedor se comunicará por el puerto 8003
EXPOSE 8003

# 8. El comando para levantar tu servidor Django. 
# IMPORTANTE: Usamos 0.0.0.0 para que acepte conexiones desde fuera del contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8003"]