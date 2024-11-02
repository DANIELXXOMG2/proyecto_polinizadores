from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error



app = Flask(__name__, template_folder="../html/", static_folder="../front/")
       

def inicializar_bd():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='40334277'
        )
        if conexion.is_connected():
            cursor = conexion.cursor()
            
            cursor.execute("CREATE DATABASE IF NOT EXISTS insectos_polinizadores")
            
            cursor.execute("USE insectos_polinizadores")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    password_ VARCHAR(255) NOT NULL
                )
            """)
            print("Base de datos y tabla creadas o verificadas correctamente.")
    except Error as e:
        print("Error al inicializar la base de datos:", e)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def registrar_usuario_en_bd(nombre, email, password_):
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='40334277',
            database='insectos_polinizadores'
        )
        if conexion.is_connected():
            cursor = conexion.cursor()
            consulta = """
            INSERT INTO Usuarios (nombre, email, password_)
            VALUES (%s, %s, %s)
            """
            cursor.execute(consulta, (nombre, email, password_))
            conexion.commit()
            print("Usuario registrado con éxito.")
    except Error as e:
        print("Error al registrar el usuario:", e)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.route('/')
def register():
    return render_template('register.html')

@app.route('/index')
def index():
    return render_template('index.html')  # Asegúrate de tener este archivo en templates

@app.route('/login')
def login():
    return render_template('login.html')  # Asegúrate de tener este archivo en templates

@app.route('/categorias')
def categorias():
    return render_template('categorias.html')  # Asegúrate de tener este archivo en templates

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')  # Asegúrate de tener este archivo en templates

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')  # Asegúrate de tener este archivo en templates

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')  # Asegúrate de tener este archivo en templates


@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    nombre= request.form['nombre']
    email = request.form['email']
    password_ = request.form['password_']
    registrar_usuario_en_bd(nombre, email, password_)
    return redirect(url_for('register'))

if __name__ == "__main__":
    inicializar_bd()  
    app.run(debug=True)