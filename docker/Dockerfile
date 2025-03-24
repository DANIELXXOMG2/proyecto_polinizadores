# Etapa 1: Construcción de assets con Node (si lo necesitas para otras dependencias)
FROM node:16-alpine as frontend
WORKDIR /app 
COPY config/package.json config/package-lock.json* ./config/
RUN cd config && npm install

# Etapa 2: Construcción de la aplicación Python
FROM python:3.9-slim

# Instalar dependencias del sistema (libpq-dev para PostgreSQL, curl y unzip para descargar Font Awesome)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copiar e instalar dependencias Python
COPY app/src/requirements.txt ./requirements.txt
COPY .certs/root.crt /usr/src/app/.certs/root.crt

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script entrypoint.sh y hacerlo ejecutable
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Copiar el resto del código fuente (templates, assets, etc.)
COPY . .

# Exponer el puerto de la aplicación
EXPOSE 5000

ENV DATABASE_URL="postgresql://insectos_polinizadores_f96i_user:m2rKK33I6kXcWNPm1vEbPlafwz9qMzc5@dpg-cvgp0ujqf0us73ckrvj0-a.oregon-postgres.render.com/insectos_polinizadores_f96i"

# Configurar el entrypoint para que se ejecute el script que descargará Font Awesome si es necesario, y después la app
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
CMD ["python", "src/app.py"]