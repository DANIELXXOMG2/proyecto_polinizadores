import_error = None

try:
    from app.src.app import app
except ImportError as e:
    # Guardar el error en una variable global
    import_error = str(e)
    
    # Si hay un error al importar las dependencias de base de datos, crear una app mínima
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return jsonify({"message": "API en mantenimiento", "error": import_error})

# Este archivo sirve como punto de entrada para Vercel
# Vercel espera una función llamada "app" o una variable llamada "app" que sea una aplicación WSGI

if __name__ == "__main__":
    app.run(debug=True)