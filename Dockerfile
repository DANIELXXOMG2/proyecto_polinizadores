# Etapa 1: Construcción de assets con Node (si lo necesitas para otras dependencias)
FROM node:16-alpine as frontend
WORKDIR /app
COPY config/package.json config/package-lock.json* ./config/
RUN cd config && npm install

# Etapa 2: Construcción de la aplicación Python
FROM python:3.9-slim

# Instalar dependencias del sistema (libmariadb-dev, curl y unzip para descargar Font Awesome)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb-dev \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copiar e instalar dependencias Python
COPY src/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script entrypoint.sh y hacerlo ejecutable
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Copiar el resto del código fuente (templates, assets, etc.)
COPY . .

# Exponer el puerto de la aplicación
EXPOSE 5000

# Configurar el entrypoint para que se ejecute el script que descargará Font Awesome si es necesario, y después la app
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
CMD ["python", "src/app.py"]