from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import os
from mysql.connector import Error
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="../html/", static_folder="../front/")

app.config['GOOGLE_MAPS_API_KEY'] = 'AIzaSyCJH77ncqZk53-C7mlslENjqKceXTQIzoc'

app.secret_key = '125436987'
ADMIN_PASSWORD = "40334277"

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_password = request.args.get('key')
        if not admin_password or admin_password != ADMIN_PASSWORD:
            flash('Acceso no autorizado')
            return redirect(url_for('login2'))
        return f(*args, **kwargs)
    return decorated_function

# Ruta para el panel administrativo
@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin.html')

# Ruta para verificar contraseñas
@app.route('/admin/verificar-password', methods=['POST'])
@admin_required
def verificar_password_admin():
    email = request.form['email']
    password_to_check = request.form['password_to_check']
    
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='40334277',
            database='insectos_polinizadores'
        )
        
        if conexion.is_connected():
            cursor = conexion.cursor()
            consulta = "SELECT password_, nombre FROM usuarios WHERE email = %s"
            cursor.execute(consulta, (email,))
            resultado = cursor.fetchone()
            
            if resultado:
                password_hash = resultado[0]
                nombre_usuario = resultado[1]
                
                if check_password_hash(password_hash, password_to_check):
                    flash(f'La contraseña es correcta para el usuario {nombre_usuario}')
                else:
                    flash('La contraseña no coincide')
            else:
                flash('Usuario no encontrado')
                
    except Error as e:
        flash(f'Error: {str(e)}')
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
            
    return redirect(url_for('admin_panel'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash('Por favor inicia sesión para acceder')
            return redirect(url_for('login2'))
        return f(*args, **kwargs)
    return decorated_function

# Procesador de contexto para tener el usuario disponible en todos los templates
@app.context_processor
def utility_processor():
    def get_user():
        return session.get('nombre', None)
    return dict(get_user=get_user)

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

def verificar_usuario(email, password_):
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='40334277',
            database='insectos_polinizadores'
        )
        if conexion.is_connected():
            cursor = conexion.cursor()
            # Primero, obtener el hash almacenado para el usuario
            consulta = "SELECT password_, nombre FROM usuarios WHERE email = %s"
            cursor.execute(consulta, (email,))
            resultado = cursor.fetchone()
            
            if resultado:
                password_hash = resultado[0]
                # Usar check_password_hash para comparar la contraseña
                if check_password_hash(password_hash, password_):
                    return True
            return False
    except Error as e:
        print("Error al verificar el usuario:", e)
        return False
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


""" 
def verificar_usuario(email, password_):
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='40334277',
            database='insectos_polinizadores'
        )
        if conexion.is_connected():
            cursor = conexion.cursor()
            consulta = "SELECT * FROM usuarios WHERE email = %s AND password_ = %s"
            print(consulta)
            cursor.execute(consulta, (email, password_))
            usuario = cursor.fetchone()
            return usuario is not None
    except Error as e:
        print("Error al verificar el usuario:", e)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
    return False """


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
            hashed_password = generate_password_hash(password_, method='pbkdf2:sha256')
            consulta = """
            INSERT INTO Usuarios (nombre, email, password_)
            VALUES (%s, %s, %s)
            """
            cursor.execute(consulta, (nombre, email, hashed_password))
            conexion.commit()
            print("Usuario registrado con éxito.")
            return True
    except Error as e:
        print("Error al registrar el usuario:", e)
        return False
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


@app.route('/')
def login2():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/contacto')
@login_required
def contacto(): 
    return render_template('contacto.html')

@app.route('/reviews')
@login_required
def reviews():
    return render_template('reviews.html')

@app.route('/sobre')
@login_required
def sobre():
    return render_template('sobre.html', api_key=app.config['GOOGLE_MAPS_API_KEY'])


@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    nombre= request.form['nombre']
    email = request.form['email']
    password_ = request.form['password_']
    registrar_usuario_en_bd(nombre, email, password_)
    return redirect(url_for('login2'))

@app.route('/login', methods=['GET','POST'])
def login():
    email = request.form['email'] 
    password_ = request.form['password_'] 
    
    if verificar_usuario(email, password_):
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='40334277',
            database='insectos_polinizadores'
        )
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone() 
        nombre = usuario[0] if usuario else None
        
        session['email'] = email  
        session['nombre'] = nombre
        
        cursor.close()
        conexion.close()
        
        flash('Inicio de sesión exitoso')
        return redirect(url_for('index'))  
    else:
        flash('Correo o contraseña incorrectos')
        return redirect(url_for('login2'))


""" @app.route('/login', methods=['GET','POST'])
def login():
    email = request.form['email'] 
    password_ = request.form['password_'] 
    
    if verificar_usuario(email, password_):
        
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='40334277',
            database='insectos_polinizadores'
        )
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone() 
        nombre = usuario[0] if usuario else None
        
        session['email'] = email  
        session['nombre'] = nombre
        
        flash('Inicio de sesión exitoso')
        return redirect(url_for('index'))  
    else:
        flash('Correo o contraseña incorrectos')
        return redirect(url_for('login2')) """

@app.route('/logout')
def logout():
    session.clear()  # Esto eliminará todas las variables de sesión
    flash('Has cerrado sesión exitosamente')
    return redirect(url_for('login2'))

if __name__ == "__main__":
    inicializar_bd()  
    app.run(debug=True)
