#!/bin/bash
set -e

# Verificar si la carpeta fontawesome existe en app/assets
if [ ! -d "/usr/src/app/assets/fontawesome" ]; then
    echo "La carpeta fontawesome no existe. Descargando e instalando FontAwesome..."
    
    # Crear directorio temporal para la descarga
    mkdir -p /tmp/fontawesome
    
    # Descargar la última versión de FontAwesome
    curl -L -o /tmp/fontawesome.zip https://use.fontawesome.com/releases/v6.4.0/fontawesome-free-6.4.0-web.zip
    
    # Descomprimir en el directorio temporal
    unzip -q /tmp/fontawesome.zip -d /tmp/fontawesome
    
    # Crear el directorio de destino si no existe
    mkdir -p /usr/src/app/assets/fontawesome
    
    # Mover los archivos al directorio de destino
    mv /tmp/fontawesome/fontawesome-free-6.4.0-web/* /usr/src/app/assets/fontawesome/
    
    # Limpiar archivos temporales
    rm -rf /tmp/fontawesome /tmp/fontawesome.zip
    
    echo "FontAwesome ha sido instalado correctamente en app/assets/fontawesome."
fi

# Ejecutar el comando especificado o el predeterminado
exec "$@"
