from flask import url_for, redirect, session, request, flash
import database as dbase
from bson.objectid import ObjectId
from bson import Binary


db = dbase.dbConnection()
def init_usuario(app):
    #GUARDAR DATOS
    @app.route('/Añadir_medicaciones', methods=['POST'])
    def Añadir_medicaciones():
        if 'correo' in session:
            id_historial = request.form.get('id_historial')
            nombre = request.form['nombre_medicamento']
            dosis = request.form['dosis']
            frecuencia = request.form['frecuencia']

            try:
                # Convertir id_historial a ObjectId
                id_historial = ObjectId(id_historial)
            except Exception as e:
                flash('Error al convertir el ID del historial clínico')
                return redirect(url_for('index'))

            # Buscar el historial clínico por su _id en la base de datos
            historial_clinico = db['historial_clinico'].find_one({'_id': id_historial})

            # Verificar si el historial clínico existe en la base de datos
            if historial_clinico is not None:
                print("historial_clinico encontrado:")
                print(historial_clinico)  # Historial clínico obtenido de la base de datos

                # Verificar si el campo de medicaciones existe y es una lista
                if 'medicaciones' in historial_clinico and isinstance(historial_clinico['medicaciones'], list):
                    # Obtener la lista actual de medicaciones
                    lista_medicaciones = historial_clinico['medicaciones']
                    
                    # Agregar el nuevo medicamento a la lista
                    lista_medicaciones.append({
                        'nombre_del_medicamento': nombre,
                        'dosis': dosis,
                        'frecuencia': frecuencia,
                    })
                    
                    # Actualizar el campo 'medicaciones' con la lista actualizada
                    db['historial_clinico'].update_one(
                        {'_id': id_historial},
                        {'$set': {'medicaciones': lista_medicaciones}}
                    )
                else:
                    # Si no existen medicaciones o no es una lista, crear el campo como una lista con el nuevo medicamento
                    db['historial_clinico'].update_one(
                        {'_id': id_historial},
                        {'$set': {'medicaciones': [{
                            'nombre_del_medicamento': nombre,
                            'dosis': dosis,
                            'frecuencia': frecuencia,
                        }]}}
                    )

                flash('Datos de medicaciones actualizados exitosamente')
                return redirect(url_for('paciente'))
            else:
                flash('Historial clínico no encontrado en la base de datos')
        else:
            flash('Usuario no ha iniciado sesión')
        
        return redirect(url_for('login'))
    
    
    @app.route('/Añadir_consulta', methods=['POST'])
    def Añadir_consulta():
        if 'correo' in session:
            id_historial = request.form.get('id_historial')
            fecha = request.form['fecha_consulta']
            motivo = request.form['motivo']
            diagnostico = request.form['diagnostico']
            tratamiento = request.form['tratamiento']

            try:
                # Convertir id_historial a ObjectId
                id_historial = ObjectId(id_historial)
            except Exception as e:
                flash('Error al convertir el ID del historial clínico')
                return redirect(url_for('paciente'))

            # Buscar el historial clínico por su _id en la base de datos
            historial_clinico = db['historial_clinico'].find_one({'_id': id_historial})

            # Obtener la lista actual de consultas médicas
            consultas_medicas = historial_clinico['registro_consultas_medicas']
                    
            # Agregar la nueva consulta médica a la lista
            consultas_medicas.append({
                'fecha': fecha,
                'motivo': motivo,
            'diagnostico': diagnostico,
                'tratamiento': tratamiento,
            })
                    
            # Actualizar el campo 'registro_consultas_medicas' con la lista actualizada
            db['historial_clinico'].update_one(
                {'_id': id_historial},
                {'$set': {'registro_consultas_medicas': consultas_medicas}}
            )
            flash('Registro de consulta médica actualizado exitosamente')
            return redirect(url_for('paciente'))
        else:
            flash('Usuario no ha iniciado sesión')

        return redirect(url_for('login'))
    
    
    @app.route('/Añadir_resultado_laboratorio', methods=['POST'])
    def Añadir_resultado_laboratorio():
        if 'correo' in session:
            id_historial = request.form.get('id_historial')
            tipo_laboratorio = request.form['tipo_laboratorio']
            resultado_laboratorio = request.form['resultado_laboratorio']

            try:
                # Convertir id_historial a ObjectId
                id_historial = ObjectId(id_historial)
            except Exception as e:
                flash('Error al convertir el ID del historial clínico')
                return redirect(url_for('paciente'))
            
            # Obtener el archivo PDF
            documento_laboratorio = request.files['documento_laboratorio']
            
            # Verificar si se cargó un archivo y si es PDF o JPG
            if documento_laboratorio:
                if documento_laboratorio.filename.endswith('.pdf') or documento_laboratorio.filename.endswith('.jpg'):
                    documento_laboratorio_data = documento_laboratorio.read()
                    documento_laboratorio_bin = Binary(documento_laboratorio_data)
                else:
                    flash('El archivo debe ser PDF o JPG')
                    return redirect(url_for('paciente'))
            else:
                documento_laboratorio_bin = None
            
            # Buscar el historial clínico por su _id en la base de datos
            historial_clinico = db['historial_clinico'].find_one({'_id': id_historial}) 

            # Verificar si ya existe una lista de resultados de laboratorio
            if 'resultados_laboratorio' in historial_clinico['examenes_pruebas_medicas']:
            # Agregar el nuevo resultado de laboratorio
                historial_clinico['examenes_pruebas_medicas']['resultados_laboratorio'].append({
                    'tipo': tipo_laboratorio,
                    'resultado': resultado_laboratorio,
                    'documento': documento_laboratorio_bin  # Guardar el archivo como binario
                })
            else:
            # Crear la lista de resultados de laboratorio y agregar el primer resultado
                historial_clinico['examenes_pruebas_medicas']['resultados_laboratorio'] = [{
                    'tipo': tipo_laboratorio,
                    'resultado': resultado_laboratorio,
                    'documento': documento_laboratorio_bin  # Guardar el archivo como binario
                }]

            print("historial_clinico actualizado:")
            print(historial_clinico)  # Mostrar historial clínico actualizado

            # Guardar el historial clínico actualizado en la base de datos
            result = db['historial_clinico'].update_one(
                {'_id': id_historial},
                {'$set': historial_clinico}
            )
            print("Resultado de db.save():")
            print(result)  # Resultado de db.save()

            flash('Resultado de laboratorio añadido exitosamente')
            return redirect(url_for('paciente'))
        else:
            flash('Usuario no ha iniciado sesión')
        
        return redirect(url_for('login'))
    
    
    @app.route('/Añadir_imagenes_medicas', methods=['POST'])
    def Añadir_imagenes_medicas():
        if 'correo' in session:
            id_historial = request.form.get('id_historial')
            tipo_imagen = request.form['tipo_imagen']
            resultado_imagen = request.form['resultado_imagen']

            try:
                # Convertir id_historial a ObjectId
                id_historial = ObjectId(id_historial)
            except Exception as e:
                flash('Error al convertir el ID del historial clínico')
                return redirect(url_for('paciente'))

            # Obtener el archivo JPG
            imagen_medica = request.files['imagen_medica']

            # Verificar si se cargó un archivo y si es un JPG
            if imagen_medica and imagen_medica.filename.endswith('.jpg'):
                imagen_medica_data = imagen_medica.read()
                imagen_medica_bin = Binary(imagen_medica_data)
            else:
                flash('El archivo debe ser JPG')
                return redirect(url_for('paciente'))

            # Buscar el historial clínico por su _id en la base de datos
            historial_clinico = db['historial_clinico'].find_one({'_id': id_historial})

            if historial_clinico:
                print("historial_clinico encontrado:")
                print(historial_clinico)  # Historial clínico obtenido de la base de datos

                # Verificar si el campo de exámenes y pruebas médicas existe
                historial_clinico.setdefault('examenes_pruebas_medicas', {}).setdefault('imagenes_medicas', [])

                # Agregar la nueva imagen médica
                historial_clinico['examenes_pruebas_medicas']['imagenes_medicas'].append({
                    'tipo': tipo_imagen,
                    'resultado': resultado_imagen,
                    'imagen': imagen_medica_bin  # Guardar el archivo como binario
                })

                print("historial_clinico actualizado:")
                print(historial_clinico)  # Mostrar historial clínico actualizado

                # Guardar el historial clínico actualizado en la base de datos
                result = db['historial_clinico'].update_one(
                    {'_id': id_historial},
                    {'$set': historial_clinico}
                )
                print("Resultado de db.save():")
                print(result)  # Resultado de db.save()

                flash('Imagen médica añadida exitosamente')
            else:
                flash('Historial clínico no encontrado en la base de datos')
        else:
            flash('Usuario no ha iniciado sesión')

        return redirect(url_for('mi_historial'))
    
    @app.route('/Añadir_vacuna', methods=['POST'])
    def Añadir_vacuna():
        if 'correo' in session:
            id_historial = request.form.get('id_historial')     
            try:
                # Convertir id_historial a ObjectId
                id_historial = ObjectId(id_historial)
            except Exception as e:
                flash('Error al convertir el ID del historial clínico')
                return redirect(url_for('paciente'))

            # Buscar el historial clínico por su _id en la base de datos
            historial_clinico = db['historial_clinico'].find_one({'_id': id_historial})
    
            # Obtener la lista actual de consultas médicas
            registro_vacunas = historial_clinico['registro_vacunas']
                    
            # Agregar la nueva registro_vacunas a la lista
            registro_vacunas.append({
                'nombre_vacuna' : request.form['nombre_vacuna'],
                'fecha_administracion' : request.form['fecha_administracion'],
                'fecha_primer_refuerzo' : request.form['fecha_primer_refuerzo'],
                'fecha_segundo_refuerzo' : request.form['fecha_segundo_refuerzo'],
                'fecha_tercer_refuerzo' : request.form['fecha_tercer_refuerzo']
            })
                    
            # Actualizar el campo 'registro_vacunas' con la lista actualizada
            db['historial_clinico'].update_one(
                {'_id': id_historial},
                {'$set': {'registro_vacunas': registro_vacunas}}
            )
            
            flash('Registro de vacunas actualizado exitosamente')
            return redirect(url_for('paciente'))
        else:
            flash('Usuario no ha iniciado sesión')

        return redirect(url_for('login'))
    
    
    @app.route('/Estilo_vida', methods=['POST'])
    def Estilo_vida():
        if 'correo' in session:
            id_historial = request.form.get('id_historial')

            try:
                # Convertir id_historial a ObjectId
                id_historial = ObjectId(id_historial)
            except Exception as e:
                flash('Error al convertir el ID del historial clínico')
                return redirect(url_for('paciente'))

            # Buscar el historial clínico por su _id en la base de datos
            historial_clinico = db.get_collection('historial_clinico').find_one({'_id': id_historial})

            # Actualizar los campos de antecedentes médicos con los nuevos valores
            historial_clinico['estilo_vida']['hace_ejercicio'] = request.form['ejercicio']
            historial_clinico['estilo_vida']['frecuencia_hace_ejercicio'] = request.form['frecuencia_ejercicio']
            historial_clinico['estilo_vida']['consumo_alcohol'] = request.form['alcohol']
            historial_clinico['estilo_vida']['frecuencia_consumo_alcohol'] = request.form['frecuencia_alcohol']
            historial_clinico['estilo_vida']['consumo_tabaco'] = request.form['tabaco']
            historial_clinico['estilo_vida']['frecuencia_consumo_tabaco'] = request.form['frecuencia_tabaco']
            historial_clinico['estilo_vida']['nivel_estres'] = request.form['nivel_estres']

            print("historial_clinico actualizado:")
            print(historial_clinico)  # Mostrar historial clínico actualizado

                # Guardar el historial clínico actualizado en la base de datos
            result = db.get_collection('historial_clinico').update_one(
                {'_id': id_historial},
                {'$set': historial_clinico}
            )
            print("Resultado de db.save():")
            print(result)  # Resultado de db.save()
            flash('Datos de antecedentes médicos actualizados exitosamente')
        else:
            flash('Usuario no ha iniciado sesión')
        
        return redirect(url_for('paciente'))
    
    @app.route('/Contacto_emergencia', methods=['POST'])
    def Contacto_emergencia():
        if 'correo' in session:
            id_historial = request.form.get('id_historial')

            try:
                # Convertir id_historial a ObjectId
                id_historial = ObjectId(id_historial)
            except Exception as e:
                flash('Error al convertir el ID del historial clínico')
                return redirect(url_for('paciente'))

            # Buscar el historial clínico por su _id en la base de datos
            historial_clinico = db.get_collection('historial_clinico').find_one({'_id': id_historial})
            # Verificar si el campo de antecedentes médicos existe
            if 'contacto_emergencia' in historial_clinico:
                # Actualizar los campos de antecedentes médicos con los nuevos valores
                historial_clinico['contacto_emergencia']['nombre_contacto'] = request.form['nombre_contacto']
                historial_clinico['contacto_emergencia']['telefono_contacto'] = request.form['telefono_contacto']
                historial_clinico['contacto_emergencia']['relacion_con_paciente'] = request.form['relacion_contacto']
            else:
                print("Contacto de emergencia no guardado")

            print("historial_clinico actualizado:")
            print(historial_clinico)  # Mostrar historial clínico actualizado

                # Guardar el historial clínico actualizado en la base de datos
            result = db.get_collection('historial_clinico').update_one(
                {'_id': id_historial},
                {'$set': historial_clinico}
            )
            print("Resultado de db.save():")
            print(result)  # Resultado de db.save()
            flash('Datos de antecedentes médicos actualizados exitosamente')
        else:
            flash('Usuario no ha iniciado sesión')
        
        return redirect(url_for('paciente'))



