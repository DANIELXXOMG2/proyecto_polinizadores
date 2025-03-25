import os
import sys
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from functools import wraps

# Bloquear archivos .pyc y configuración de módulos
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Determinar la base path según el entorno (local o Vercel)
basedir = os.path.abspath(os.path.dirname(__file__))
is_vercel = os.environ.get('VERCEL', False)

# Ajustar rutas según el entorno
if is_vercel:
    template_dir = os.path.abspath(os.path.join(basedir, '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(basedir, '..', 'assets'))
    dot_env_path = os.path.abspath(os.path.join(basedir, '..', '..', '.env'))
else:
    template_dir = os.path.abspath(os.path.join(basedir, '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(basedir, '..', 'assets'))
    dot_env_path = os.path.abspath(os.path.join(basedir, '..', '..', '.env'))

# Inicialización de Flask
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.environ.get('SECRET_KEY', '125436987')

# Ruta para servir archivos estáticos directamente
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(static_dir, filename)

# Directorio para almacenar imágenes de perfil
UPLOAD_FOLDER = os.path.join(app.root_path, '..', 'usericons')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# En Vercel, usaremos /tmp para almacenamiento temporal
if is_vercel:
    UPLOAD_FOLDER = '/tmp'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Cargar variables de entorno desde .env
if os.path.exists(dot_env_path):
    load_dotenv(dot_env_path)
else:
    load_dotenv()  # Intenta cargar desde el directorio actual

# Configuración de la base de datos
if is_vercel:
    # En Vercel, construir la URL manualmente para asegurar la interpolación de variables
    db_user = os.getenv('DB_USER', '')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', '')
    db_name = os.getenv('DB_NAME', '')
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
else:
    # En otros entornos (como Render), usar DATABASE_URL directamente
    DATABASE_URL = os.getenv('DATABASE_URL', '')

if not DATABASE_URL:
    print("La variable de entorno DATABASE_URL no está definida.")
    if not is_vercel:  # Solo salir si no estamos en Vercel
        exit(1)

# Configuración de la base de datos condicionada al entorno
if DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"application_name": "polinizadores_app"})
    Session = sessionmaker(bind=engine)
else:
    print("Advirtiendo: Sin conexión a base de datos")
    # Modo simulado para desarrollo o entornos sin base de datos
    engine = None
    Session = None

# Función para verificar si la sesión ha expirado
def check_session_timeout():
    if 'last_activity' in session:
        inactive_time = datetime.now() - datetime.fromisoformat(session['last_activity'])
        if inactive_time > timedelta(minutes=30):
            session.clear()
            return True
    session['last_activity'] = datetime.now().isoformat()
    return False

# Decorador para requerir inicio de sesión
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash('Por favor inicia sesión para acceder.')
            return redirect(url_for('login2'))
        if check_session_timeout():
            flash('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.')
            return redirect(url_for('login2'))
        return f(*args, **kwargs)
    return decorated_function

# Procesador de contexto para acceso global a datos de usuario
@app.context_processor
def utility_processor():
    def get_user():
        return session.get('nombre', None)
    return dict(get_user=get_user)

# Rutas y funcionalidades
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

@app.route('/usericons/<filename>')
def usericons_static(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    if request.method == 'POST':
        try:
            with Session() as db_session:
                result = db_session.execute(
                    text("SELECT id, nombre, email, password_ FROM Usuarios WHERE email = :email"),
                    {"email": session.get('email')}
                ).fetchone()

                if not result:
                    flash('Error: Usuario no encontrado.')
                    return redirect(url_for('logout'))

                nuevo_nombre = request.form.get('nombre')
                nuevo_email = request.form.get('email')
                nueva_password = request.form.get('nueva_password')
                password_actual = request.form.get('password_actual')

                # Verificar contraseña actual
                if password_actual and not check_password_hash(result[3], password_actual):
                    flash('La contraseña actual no es correcta.')
                    return redirect(url_for('user'))

                # Actualizar campos modificados
                if nuevo_nombre and nuevo_nombre != result[1]:
                    db_session.execute(
                        text("UPDATE Usuarios SET nombre = :nombre WHERE id = :id"),
                        {"nombre": nuevo_nombre, "id": result[0]}
                    )
                    session['nombre'] = nuevo_nombre
                    flash('Nombre actualizado.')

                if nuevo_email and nuevo_email != result[2]:
                    # Verificar si el nuevo email ya existe
                    email_exists = db_session.execute(
                        text("SELECT COUNT(*) FROM Usuarios WHERE email = :email"),
                        {"email": nuevo_email}
                    ).scalar()
                    
                    if email_exists:
                        flash('Este correo electrónico ya está en uso.')
                    else:
                        db_session.execute(
                            text("UPDATE Usuarios SET email = :email WHERE id = :id"),
                            {"email": nuevo_email, "id": result[0]}
                        )
                        session['email'] = nuevo_email
                        flash('Correo electrónico actualizado.')
                
                # Actualizar contraseña si se proporcionó una nueva y la actual fue verificada
                if nueva_password and password_actual:
                    hashed_password = generate_password_hash(nueva_password, method='pbkdf2:sha256')
                    db_session.execute(
                        text("UPDATE Usuarios SET password_ = :password WHERE id = :id"),
                        {"password": hashed_password, "id": result[0]}
                    )
                    flash('Contraseña actualizada correctamente.')

                if 'imagen_perfil' in request.files:
                    file = request.files['imagen_perfil']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(f"{session['nombre']}_{file.filename}")
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        file.save(filepath)
                        db_session.execute(
                            text("UPDATE Usuarios SET imagen_perfil = :imagen_perfil WHERE id = :id"),
                            {"imagen_perfil": filename, "id": result[0]}
                        )
                        db_session.commit()

                return redirect(url_for('user'))
        except Exception as e:
            flash(f'Error al actualizar perfil: {str(e)}.')
            return redirect(url_for('user'))

    try:
        if Session is None:  # Modo sin base de datos
            result = {'nombre': session.get('nombre', 'Usuario de prueba'), 
                     'email': session.get('email', 'test@example.com'), 
                     'imagen_perfil': None}
        else:
            with Session() as db_session:
                result = db_session.execute(
                    text("SELECT nombre, email, imagen_perfil FROM Usuarios WHERE email = :email"),
                    {"email": session.get('email')}
                ).fetchone()

                if not result:
                    flash('Error: Usuario no encontrado.')
                    return redirect(url_for('logout'))
        
        return render_template('/usuarios/user.html', 
                            nombre=result[0] if not isinstance(result, dict) else result['nombre'],
                            email=result[1] if not isinstance(result, dict) else result['email'],
                            imagen_perfil=result[2] if not isinstance(result, dict) else result['imagen_perfil'])
    except Exception as e:
        flash(f'Error al obtener datos: {str(e)}.')
        return redirect(url_for('index'))

# Resto de rutas...
@app.route('/agregar_comentario', methods=['POST'])
@login_required
def agregar_comentario():
    contenido = request.form.get('contenido')
    if not contenido:
        flash('El comentario no puede estar vacío.')
        return redirect(url_for('reviews'))

    try:
        if Session is not None:
            with Session() as db_session:
                db_session.execute(
                    text("""
                        INSERT INTO comentarios (usuario_id, nombre_usuario, contenido)
                        VALUES (:usuario_id, :nombre_usuario, :contenido)
                    """),
                    {
                        "usuario_id": session['user_id'],
                        "nombre_usuario": session['nombre'],
                        "contenido": contenido
                    }
                )
                db_session.commit()
                flash('Comentario agregado exitosamente.')
        else:
            # Modo sin base de datos
            flash('Comentario simulado agregado (modo sin base de datos).')
    except Exception as e:
        flash(f'Error al agregar el comentario: {str(e)}.')

    return redirect(url_for('reviews'))

@app.route('/reviews')
@login_required
def reviews():
    try:
        if Session is None:  # Modo sin base de datos
            comentarios = []
        else:
            with Session() as db_session:
                result = db_session.execute(
                    text("""
                        SELECT nombre_usuario, contenido, fecha_creacion
                        FROM comentarios
                        ORDER BY fecha_creacion DESC
                    """)
                ).fetchall()

                comentarios = [{"nombre_usuario": r[0], "contenido": r[1], "fecha_creacion": r[2]} for r in result]

        return render_template('/contenido/reviews.html', comentarios=comentarios)
    except Exception as e:
        flash(f'Error al cargar los comentarios: {str(e)}.')
        return render_template('/contenido/reviews.html', comentarios=[])

@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    nombre = request.form.get('nombre')
    email = request.form.get('email')
    password_ = request.form.get('password_')
    ip_address = request.remote_addr

    # Verificar que se hayan enviado todos los datos
    if not all([nombre, email, password_]):
        flash('Todos los campos son obligatorios.')
        return redirect(url_for('register'))

    try:
        if Session is None:  # Modo sin base de datos
            # En entornos sin DB, simular un registro exitoso
            flash('Registro simulado exitoso (modo sin base de datos). Por favor inicia sesión.', 'success')
            return redirect(url_for('login2'))
        
        with Session() as db_session:
            # Se genera el hash de la contraseña y se inserta el usuario en la base de datos
            hashed_password = generate_password_hash(password_, method='pbkdf2:sha256')
            db_session.execute(
                text("""
                    INSERT INTO Usuarios (nombre, email, password_)
                    VALUES (:nombre, :email, :password_)
                """),
                {"nombre": nombre, "email": email, "password_": hashed_password}
            )
            db_session.commit()
            # Obtener el id del usuario insertado y registrar la IP
            usuario_id = db_session.execute(text("SELECT LASTVAL()")).scalar()
            registrar_ip(usuario_id, nombre, ip_address)

        # Mensaje de éxito y redirección inmediata al login
        flash('¡Registro exitoso! Por favor inicia sesión.', 'success')
        return redirect(url_for('login2'))
    except Exception as e:
        if Session is not None:
            db_session.rollback()
        flash(f'Error en el registro: {str(e)}', 'error')
        return redirect(url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password_ = request.form.get('password_')
        ip_address = request.remote_addr

        if not all([email, password_]):
            flash('Todos los campos son obligatorios.')
            return redirect(url_for('login2'))

        try:
            if Session is None:  # Modo sin base de datos
                # En entorno de desarrollo/demostración, permitir cualquier login
                session.permanent = True
                session['email'] = email
                session['nombre'] = email.split('@')[0]  # Usar parte del email como nombre
                session['user_id'] = 1
                session['last_activity'] = datetime.now().isoformat()

                flash('Inicio de sesión simulado exitoso (modo sin base de datos).')
                return redirect(url_for('index'))
                
            with Session() as db_session:
                result = db_session.execute(
                    text("SELECT id, nombre, email, password_ FROM Usuarios WHERE email = :email"),
                    {"email": email}
                ).fetchone()

                if result and check_password_hash(result[3], password_):
                    registrar_ip(result[0], result[1], ip_address)

                    session.permanent = True
                    session['email'] = email
                    session['nombre'] = result[1]
                    session['user_id'] = result[0]
                    session['last_activity'] = datetime.now().isoformat()

                    flash('Inicio de sesión exitoso.')
                    return redirect(url_for('index'))
                else:
                    flash('Correo o contraseña incorrectos.')
                    return redirect(url_for('login2'))
        except Exception as e:
            flash(f'Error al iniciar sesión: {str(e)}.')
            return redirect(url_for('login2'))

    return redirect(url_for('login2'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.')
    return redirect(url_for('login2'))

@app.route('/sobre')
@login_required
def sobre():
    return render_template('/contenido/sobre.html')

@app.route('/animales')
def animales():
    return render_template('/contenido/animals.html')

@app.route('/animals')
def animals_redirect():
    return redirect(url_for('animales'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('/errores/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('/errores/500.html'), 500

# Función para registrar IP de un usuario
def registrar_ip(usuario_id, nombre, ip_address):
    if Session is None:  # Saltar en modo sin base de datos
        return
    
    try:
        with Session() as db_session:
            db_session.execute(
                text("""
                    INSERT INTO registro_ips (usuario_id, nombre, ip_address)
                    VALUES (:usuario_id, :nombre, :ip_address)
                """),
                {"usuario_id": usuario_id, "nombre": nombre, "ip_address": ip_address}
            )
            db_session.commit()
    except Exception as e:
        print(f"Error al registrar IP: {str(e)}")

# Solo ejecutar esto si corremos directamente, no cuando importamos en Vercel
if __name__ == "__main__":
    # Ejecutar el script SQL para crear tablas e insertar datos
    if engine:
        with engine.connect() as connection:
            with open(os.path.join(basedir, 'registros.sql'), 'r') as sql_file:           
                sql_script = sql_file.read()
                connection.execute(text(sql_script))
        print("Base de datos y tablas creadas correctamente.")
    
    app.run(host="0.0.0.0", debug=True)