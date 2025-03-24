#!/bin/bash

# Instalar primero psycopg2-binary (versión precompilada)
pip install --no-cache-dir psycopg2-binary==2.8.6

# Instalar el resto de las dependencias usando el archivo simplificado
pip install --no-cache-dir -r vercel_requirements.txt 