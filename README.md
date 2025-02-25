# Proyecto Polinizadores

Este proyecto es una aplicación web diseñada para gestionar información sobre polinizadores. Utiliza tecnologías modernas como Tailwind CSS para el diseño y Alpine.js para la interactividad en el frontend. La aplicación se ejecuta en un contenedor Docker, lo que facilita su despliegue y configuración.

## Estructura del Proyecto

El proyecto tiene la siguiente estructura de archivos:

```
proyecto_polinizadores
├── config
│   ├── .env                # Variables de entorno necesarias para la configuración de la aplicación
│   ├── package.json        # Configuración de npm y dependencias del proyecto
│   └── tailwind.config.js  # Configuración de Tailwind CSS
├── src
│   └── app.js             # Punto de entrada de la aplicación
├── Dockerfile              # Instrucciones para construir la imagen de Docker
├── docker-compose.yml      # Configuración de los servicios de la aplicación
└── .vscode
    └── settings.json       # Configuraciones específicas del entorno de desarrollo
```

## Requisitos

- Node.js
- Docker
- Docker Compose

## Configuración

1. Clona el repositorio:
   ```
   git clone <URL_DEL_REPOSITORIO>
   cd proyecto_polinizadores
   ```

2. Crea un archivo `.env` en la carpeta `config` y agrega tus variables de entorno. Un ejemplo de configuración se encuentra en `config/.env`.

3. Construye la imagen de Docker:
   ```
   docker-compose build
   ```

4. Inicia los servicios:
   ```
   docker-compose up
   ```

## Uso

Una vez que los servicios estén en funcionamiento, puedes acceder a la aplicación en `http://localhost:5501`.

Google Maps Api key: 
GOOGLE_MAPS_API_KEY=AIzaSyCJH77ncqZk53-C7mlslENjqKceXTQIzoc

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.