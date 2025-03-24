from app.src.app import app
from flask import Flask, request

# Este archivo sirve como punto de entrada para Vercel
# Vercel espera una función llamada "app" o una variable llamada "app" que sea una aplicación WSGI

if __name__ == "__main__":
    app.run(debug=True)