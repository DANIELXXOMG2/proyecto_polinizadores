#!/bin/sh
set -e
# Definir el directorio de destino donde queremos tener Font Awesome (que se mapea con tu carpeta local ./assets)
TARGET_DIR="/usr/src/app/assets/fontawesome"

# Si no existe la carpeta deseada, se descarga y se extrae Font Awesome, y se renombra la carpeta extraída
if [ ! -d "$TARGET_DIR" ]; then
  echo "Descargando FontAwesome..."
  curl -L -o fontawesome.zip "https://use.fontawesome.com/releases/v6.7.2/fontawesome-free-6.7.2-web.zip"
  mkdir -p /usr/src/app/assets
  unzip fontawesome.zip -d /usr/src/app/assets
  rm fontawesome.zip
  # Renombrar la carpeta descargada al nombre deseado
  mv /usr/src/app/assets/fontawesome-free-6.7.2-web "$TARGET_DIR"
fi
exec "$@"