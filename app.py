from io import BytesIO
from flask import Flask, render_template, url_for, redirect, session, request, flash
import bcrypt
import database as dbase
from routes import init_routes
from paciente_insert import init_usuario
from paciente_update import init_usuario_update
from paciente_delete import init_usuario_delete
db = dbase.dbConnection()
import base64
from bson.objectid import ObjectId
from flask import send_file
from logic import nocache, obtener_doctor, obtener_usuario_por_numero_social, obtener_historial_clinico, generar_captcha
app = Flask(__name__)
app.secret_key = 'M0i1Xc$GfPw3Yz@2SbQ9lKpA5rJhDtE7'
init_routes(app)
init_usuario(app)
init_usuario_update(app)
init_usuario_delete(app)
###############################################################


@app.route('/buscar_usuario', methods=['GET', 'POST'])
@nocache
def buscar_usuario():
    correo = session.get('correo')
    if correo:
        # Verificar si el usuario es un admin en tu sistema
        usuario = obtener_doctor(correo)
        if usuario and usuario['es_admin']:
            if request.method == 'POST':
                numero_social = request.form['numero_social']

                # Buscar en la base de datos el usuario por número de seguro social
                usuario_encontrado = obtener_usuario_por_numero_social(numero_social)

                if usuario_encontrado:
                    # Usuario encontrado, obtener su historial clínico
                    historial_clinico = obtener_historial_clinico(usuario_encontrado['_id'])
                    return render_template('admin.html', usuario=usuario_encontrado, historial_clinico=historial_clinico)
                else:
                    flash('No se encontró información para el número de seguro social proporcionado.')

            # Si es GET o si no se encontró el usuario, mostrar el formulario de búsqueda
            return render_template('buscar_usuario.html')

    # Si no es un admin o no hay sesión iniciada, redirigir al login
    return redirect(url_for('login'))



@app.route('/descargar_documento/<string:usuario_id>')
def descargar_documento(usuario_id):
    # Buscar el historial clínico por su _id en la base de datos
    historial_clinico = db['historial_clinico'].find_one({'_id': ObjectId(usuario_id)})

    # Verificar si el historial clínico y los resultados de laboratorio existen
    if historial_clinico and 'examenes_pruebas_medicas' in historial_clinico and \
            'resultados_laboratorio' in historial_clinico['examenes_pruebas_medicas']:

        # Obtener el primer resultado de laboratorio que tenga un documento adjunto
        for resultado in historial_clinico['examenes_pruebas_medicas']['resultados_laboratorio']:
            if resultado.get('documento'):
                # Obtener el contenido binario del documento
                documento_bin = resultado['documento']
                # Crear un objeto BytesIO para almacenar el contenido binario
                documento_stream = BytesIO(documento_bin)
                # Enviar el contenido binario como un archivo adjunto
                documento_stream.seek(0)  # Asegurar que la posición del cursor esté al inicio del archivo
                return send_file(documento_stream, mimetype='application/pdf', as_attachment=True, download_name='documento.pdf')

        # Si no se encontró ningún documento adjunto en los resultados de laboratorio
        flash('Documento no encontrado')
    else:
        flash('Historial clínico o resultado de laboratorio no encontrado')

    # Redirigir a la página principal si hay un error o el documento no está disponible
    return redirect(url_for('mi_historial'))



@app.route('/descargar_imagen/<string:usuario_id>')
def descargar_imagen(usuario_id):
    # Buscar el historial clínico por su _id en la base de datos
    historial_clinico = db['historial_clinico'].find_one({'_id': ObjectId(usuario_id)})

    # Verificar si el historial clínico y las imagenes medicas existen
    if historial_clinico and 'examenes_pruebas_medicas' in historial_clinico and \
            'imagenes_medicas' in historial_clinico['examenes_pruebas_medicas']:

        # Obtener la primera imagen medica que tenga un documento adjunto
        for resultado in historial_clinico['examenes_pruebas_medicas']['imagenes_medicas']:
            if resultado.get('imagen'):
                # Decodificar los datos base64 de la imagen a binario
                imagen_base64 = resultado['imagen']
                try:
                    imagen_bin = base64.b64decode(imagen_base64)
                except Exception as e:
                    flash('Error al decodificar la imagen')
                    return redirect(url_for('mi_historial'))

                # Crear un objeto BytesIO para almacenar el contenido binario
                imagen_stream = BytesIO(imagen_bin)
                # Enviar el contenido binario como un archivo adjunto
                imagen_stream.seek(0)  # Asegurar que la posición del cursor esté al inicio del archivo
                return send_file(imagen_stream, mimetype='image/jpeg', as_attachment=True, download_name='resultado.jpg')

        # Si no se encontró ningún documento adjunto en los resultados de laboratorio
        flash('Imagen no encontrada')
    else:
        flash('Historial clínico o imagenes medicas no encontrado')

    # Redirigir a la página principal si hay un error o la imagen no está disponible
    return redirect(url_for('mi_historial'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        password = request.form.get('password')
        captcha_ingresado = request.form.get('captcha')

        # Verificar CAPTCHA
        captcha_real = session.get('captcha')
        if not captcha_real or captcha_ingresado.upper() != captcha_real:
            flash('CAPTCHA incorrecto. Inténtalo de nuevo.')
            # Generar y mostrar nuevo CAPTCHA en el formulario
            captcha_text = generar_captcha()
            return render_template('login.html', captcha=captcha_text, message='CAPTCHA incorrecto. Inténtalo de nuevo.')


        paciente = db['pacientes']
        doctor = db['doctor']

        # Buscar en la colección de pacientes
        login_paciente = paciente.find_one({'correo': correo})
        if login_paciente and bcrypt.checkpw(password.encode('utf-8'), login_paciente['password']):
            # Autenticación exitosa
            session['correo'] = correo
            flash('Inicio de sesión exitoso como paciente.')
            return redirect(url_for('paciente'))
            

        # Buscar en la colección de doctores
        login_doctor = doctor.find_one({'correo': correo})
        if login_doctor and bcrypt.checkpw(password.encode('utf-8'), login_doctor['password']):
            # Autenticación exitosa
            session['correo'] = correo
            flash('Inicio de sesión exitoso como doctor.')
            return redirect(url_for('admin'))

        # Si no se encuentra en ninguna colección o la contraseña es incorrecta
        flash('Correo o contraseña incorrectos.', 'error')

    # Generar y mostrar CAPTCHA en el formulario de login
    captcha_data = generar_captcha()
    return render_template('login.html', captcha=captcha_data)

@app.route('/logout')
@nocache
def logout():
    session.clear()  # Elimina todas las variables de sesión
    return redirect(url_for('index'))  # Redirige al inicio de sesión


@app.route('/register/', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        correo = request.form['correo']
        existing_paciente = db['pacientes'].find_one({'correo': correo})

        if existing_paciente is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            paciente_data = {
                'nombre': request.form['nombre'],
                'numeroSocial': request.form['numeroSocial'],
                'correo': correo,
                'fecha_nacimiento': request.form['fecha'],
                'telefono': request.form['telefono'],
                'genero': request.form['genero'],
                'estado': request.form['estado'],
                'municipio': request.form['municipio'],
                'ciudad': request.form['ciudad'],
                'cp': request.form['cp'],
                'password': hashpass
            }

            paciente_id = db['pacientes'].insert_one(paciente_data).inserted_id

            historial_clinico_data = {
                "tipo": "historial_clinico",
                "usuario_id": paciente_id,
                "antecedentes_medicos": {},
                "medicaciones": {},
                "examenes_pruebas_medicas": {},
                "registro_consultas_medicas": [],
                "registro_vacunas": [],
                "estilo_vida": {},
                "contacto_emergencia": {}
            }

            db['historial_clinico'].insert_one(historial_clinico_data)

            session['correo'] = correo
            flash('Usuario registrado exitosamente')
            return redirect(url_for('login'))
        else:
            flash('El correo ya está en uso')
            return redirect(url_for('register'))

    return render_template('registro.html')

###############################################################

###############################################################


if __name__ == "__main__":
    app.run(debug=True)
