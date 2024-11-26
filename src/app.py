from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import os
import pyotp
from mysql.connector import Error
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv('config/.env')

UPLOAD_FOLDER = 'assets/img/usericon'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

app = Flask(__name__, template_folder="../templates/", static_folder="../assets/")

# Agregar al inicio de tu app.py
if not os.path.exists(os.path.join(app.static_folder, 'img/usericon')):
    os.makedirs(os.path.join(app.static_folder, 'img/usericon'))

# Configuración básica
app.config['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY')
app.secret_key = '125436987'
TOTP_SECRET = os.getenv('TOTP_SECRET')

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def check_session_timeout():
    if 'last_activity' in session:
        inactive_time = datetime.now() - datetime.fromisoformat(session['last_activity'])
        if inactive_time > timedelta(minutes=30):
            session.clear()
            return True
    session['last_activity'] = datetime.now().isoformat()
    return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash('Por favor inicia sesión para acceder')
            return redirect(url_for('login2'))
        if check_session_timeout():
            flash('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.')
            return redirect(url_for('login2'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def utility_processor():
    def get_user():
        return session.get('nombre', None)
    return dict(get_user=get_user)

@app.route('/admin')
def admin_panel():
    return render_template('/usuarios/admin.html', secret_key=TOTP_SECRET)

@app.route('/admin_login', methods=['POST'])
def admin_login():
    if not session.get('admin_attempts'):
        session['admin_attempts'] = 0
        session['last_attempt'] = datetime.now().isoformat()
    
    if session['admin_attempts'] >= 5:
        last_attempt = datetime.fromisoformat(session['last_attempt'])
        if datetime.now() - last_attempt < timedelta(minutes=1):
            flash('Demasiados intentos. Por favor, espera 15 minutos.')
            return redirect(url_for('admin_panel'))
        session['admin_attempts'] = 0

    admin_token = request.form.get('admin_token')
    totp = pyotp.TOTP(TOTP_SECRET)
    
    if totp.verify(admin_token):
        session['admin_attempts'] = 0
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            
            if conexion.is_connected():
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT id, nombre, email, password_ FROM usuarios")
                usuarios = cursor.fetchall()
                return render_template('/usuarios/admin_dashboard.html', usuarios=usuarios)
                
        except Error as e:
            flash(f'Error de base de datos: {str(e)}')
            return redirect(url_for('admin_panel'))
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()
    else:
        session['admin_attempts'] += 1
        session['last_attempt'] = datetime.now().isoformat()
        flash('Código TOTP inválido. Por favor, intenta de nuevo.')
        return redirect(url_for('admin_panel'))

def inicializar_bd():
    try:
        conexion = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        if conexion.is_connected():
            cursor = conexion.cursor()
            
            cursor.execute("CREATE DATABASE IF NOT EXISTS insectos_polinizadores")
            cursor.execute("USE insectos_polinizadores")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_ VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    imagen_perfil VARCHAR(500) DEFAULT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comentarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    nombre_usuario VARCHAR(255) NOT NULL,
                    contenido TEXT NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
                )
            """)
        
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registro_ips (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT,
                    nombre VARCHAR(255) NOT NULL,
                    ip_address VARCHAR(45) NOT NULL,
                    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
                )
            """)    
            print("Base de datos y tablas creadas correctamente.")
    except Error as e:
        print("Error al inicializar la base de datos:", e)
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()


def verificar_usuario(email, password_):
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor(dictionary=True)
            # Cambiamos la consulta para obtener más información
            consulta = "SELECT id, nombre, email, password_ FROM usuarios WHERE email = %s"
            cursor.execute(consulta, (email,))
            usuario = cursor.fetchone()
            
            if usuario and check_password_hash(usuario['password_'], password_):
                # Actualizar último login
                cursor.execute("UPDATE usuarios SET last_login = NOW() WHERE email = %s", (email,))
                conexion.commit()
                # Retornamos True y los datos del usuario
                return True, usuario
            return False, None
    except Error as e:
        print("Error al verificar el usuario:", e)
        return False, None
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

def registrar_usuario_en_bd(nombre, email, password_, ip_address):
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor()
            
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "El email ya está registrado"
            
            hashed_password = generate_password_hash(password_, method='pbkdf2:sha256')
            
            consulta = """
            INSERT INTO usuarios (nombre, email, password_)
            VALUES (%s, %s, %s)
            """
            valores = (nombre, email, hashed_password)
            cursor.execute(consulta, valores)
            conexion.commit()
            
            if cursor.rowcount > 0:
                # Obtener el ID del usuario recién registrado
                usuario_id = cursor.lastrowid
                # Registrar la IP
                registrar_ip(usuario_id, nombre, ip_address)
                return True, "Usuario registrado con éxito"
            else:
                return False, "No se pudo registrar el usuario"
                
    except Error as e:
        print(f"Error al registrar usuario: {str(e)}")
        return False, f"Error al registrar: {str(e)}"
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

def registrar_ip(usuario_id, nombre, ip_address):
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor()
            consulta = """
            INSERT INTO registro_ips (usuario_id, nombre, ip_address)
            VALUES (%s, %s, %s)
            """
            cursor.execute(consulta, (usuario_id, nombre, ip_address))
            conexion.commit()
    except Error as e:
        print(f"Error al registrar IP: {str(e)}")
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

@app.route('/')
def login2():
    return render_template('/usuarios/login.html')

@app.route('/register')
def register():
    return render_template('/usuarios/register.html')

@app.route('/index')
@login_required
def index():
    return render_template('/contenido/index.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    if request.method == 'POST':
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            
            # Obtener datos actuales del usuario para verificación
            cursor.execute("SELECT email, password_ FROM usuarios WHERE email = %s", 
                        (session.get('email'),))
            usuario_actual = cursor.fetchone()
            
            if not usuario_actual:
                flash('Error: Usuario no encontrado')
                return redirect(url_for('logout'))
            
            # Obtener datos del formulario
            nuevo_nombre = request.form.get('nombre')
            nuevo_email = request.form.get('email')
            nueva_password = request.form.get('password_')
            
            # Verificar si el nuevo email ya existe (si se está cambiando)
            if nuevo_email and nuevo_email != session.get('email'):
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s", (nuevo_email,))
                if cursor.fetchone()[0] > 0:
                    flash('El email ya está registrado por otro usuario')
                    return redirect(url_for('user'))
            
            # Construir la consulta de actualización
            update_query = "UPDATE usuarios SET "
            update_params = []
            
            if nuevo_nombre:
                update_query += "nombre = %s, "
                update_params.append(nuevo_nombre)
            
            if nuevo_email:
                update_query += "email = %s, "
                update_params.append(nuevo_email)
            
            if nueva_password:
                hashed_password = generate_password_hash(nueva_password, method='pbkdf2:sha256')
                update_query += "password_ = %s, "
                update_params.append(hashed_password)
            
            # Procesar imagen si se proporcionó una nueva
            if 'imagen_perfil' in request.files:
                file = request.files['imagen_perfil']
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{session['nombre']}_{file.filename}")
                    filepath = os.path.join(app.static_folder, 'img/usericon', filename)
                    file.save(filepath)
                    update_query += "imagen_perfil = %s, "
                    update_params.append(filename)
            
            if update_params:
                # Eliminar la última coma y agregar la condición WHERE
                update_query = update_query.rstrip(', ')
                update_query += " WHERE email = %s"
                update_params.append(session.get('email'))
                
                # Ejecutar la actualización
                cursor.execute(update_query, tuple(update_params))
                conexion.commit()
                
                # Actualizar la sesión con los nuevos datos
                if nuevo_nombre:
                    session['nombre'] = nuevo_nombre
                if nuevo_email:
                    session['email'] = nuevo_email
                
                flash('Perfil actualizado correctamente')
            
            return redirect(url_for('user'))
            
        except Error as e:
            flash(f'Error al actualizar perfil: {str(e)}')
            return redirect(url_for('user'))
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()
    
    # Para GET request
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT nombre, email, imagen_perfil FROM usuarios WHERE email = %s", 
                    (session.get('email'),))
        usuario = cursor.fetchone()
        
        if not usuario:
            flash('Error: Usuario no encontrado')
            return redirect(url_for('logout'))
        
        return render_template('/usuarios/user.html', usuario=usuario)
        
    except Error as e:
        flash(f'Error al obtener datos: {str(e)}')
        return redirect(url_for('index'))
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

@app.route('/agregar_comentario', methods=['POST'])
@login_required
def agregar_comentario():
    contenido = request.form.get('contenido')
    if not contenido:
        flash('El comentario no puede estar vacío')
        return redirect(url_for('reviews'))
    
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor()
            
            # Insertar el comentario
            consulta = """
            INSERT INTO comentarios (usuario_id, nombre_usuario, contenido)
            VALUES (%s, %s, %s)
            """
            valores = (session['user_id'], session['nombre'], contenido)
            cursor.execute(consulta, valores)
            conexion.commit()
            
            flash('Comentario agregado exitosamente')
            
    except Error as e:
        flash(f'Error al agregar el comentario: {str(e)}')
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()
    
    return redirect(url_for('reviews'))

@app.route('/reviews')
@login_required
def reviews():
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            cursor = conexion.cursor(dictionary=True)
            
            # Obtener todos los comentarios ordenados por fecha
            cursor.execute("""
                SELECT nombre_usuario, contenido, fecha_creacion 
                FROM comentarios 
                ORDER BY fecha_creacion DESC
            """)
            comentarios = cursor.fetchall()
            
            return render_template('/contenido/reviews.html', comentarios=comentarios)
            
    except Error as e:
        flash(f'Error al cargar los comentarios: {str(e)}')
        return render_template('/contenido/reviews.html', comentarios=[])
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()
            
@app.route('/sobre')
@login_required
def sobre():
    return render_template('/contenido/sobre.html', api_key=app.config['GOOGLE_MAPS_API_KEY'])

@app.route('/animals')
@login_required
def animals():
    return render_template('/contenido/animals.html')

@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    password_ = request.form.get('password_')
    ip_address = request.remote_addr
    
    if not all([nombre, email, password_]):
        flash('Todos los campos son obligatorios')
        return redirect(url_for('register'))
    
    try:
        success, message = registrar_usuario_en_bd(nombre, email, password_, ip_address)
        flash(message)
        if success:
            return redirect(url_for('login2'))
        return redirect(url_for('register'))
    except Exception as e:
        flash(f'Error en el registro: {str(e)}')
        return redirect(url_for('register'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password_ = request.form.get('password_')
        ip_address = request.remote_addr
        
        if not all([email, password_]):
            flash('Todos los campos son obligatorios')
            return redirect(url_for('login2'))
        
        success, usuario = verificar_usuario(email, password_)
        if success:
            # Registrar IP
            registrar_ip(usuario['id'], usuario['nombre'], ip_address)
            
            # Actualizar sesión con los datos más recientes
            session.permanent = True
            session['email'] = usuario['email']
            session['nombre'] = usuario['nombre']
            session['user_id'] = usuario['id']
            session['last_activity'] = datetime.now().isoformat()
            
            flash('Inicio de sesión exitoso')
            return redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos')
            return redirect(url_for('login2'))
    return redirect(url_for('login2'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente')
    return redirect(url_for('login2'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('/errores/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('/errores/500.html'), 500

if __name__ == "__main__":
    inicializar_bd()
    app.run(debug=True) 