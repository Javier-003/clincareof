from flask import url_for, redirect, session, request, flash
import database as dbase
from bson.objectid import ObjectId

db = dbase.dbConnection()
def init_usuario_update(app):
    
    #Seccion de actualizar datos
    @app.route('/Actualizar_datos', methods=['POST'])
    def Actualizar_datos():
        if 'correo' in session:
            id_usuario = request.form.get('id_usuario')
            telefono = request.form['N_telefono']
            correo = request.form['N_correo']
            estado = request.form['N_estado']
            ciudad = request.form['N_ciudad']
            municipio = request.form['N_municipio']
            cp = request.form['N_cp']
            
            # Verificar si el usuario existe en la base de datos
            usuario = db['pacientes'].find_one({'_id': ObjectId(id_usuario)})
            
            if usuario:
                # Actualizar los campos del usuario con los nuevos valores
                db['pacientes'].update_one(
                    {'_id': ObjectId(id_usuario)},
                    {
                        '$set': {
                            'telefono': telefono,
                            'correo': correo,
                            'estado': estado,
                            'municipio': municipio,
                            'ciudad': ciudad,
                            'cp': cp
                        }
                    }
                )

                flash('Datos actualizados exitosamente')
            else:
                flash('Usuario no encontrado en la base de datos')
        else:
            flash('Usuario no ha iniciado sesión')
        
        return redirect(url_for('paciente'))

    @app.route('/Actualizar_antecedentes', methods=['POST'])
    def Actualizar_antecedentes():
        if 'correo' in session:
            id_historial = request.form.get('id_historial')
            enfermedadesCronicas = request.form['N_enfermedad_cronica']
            alergias = request.form['N_alergia']
            cirugiasPrevias = request.form['N_cirugia_previa']
            traumatismosLesiones = request.form['N_traumatismo_lesion']

            try:
                # Convertir id_historial a ObjectId
                id_historial = ObjectId(id_historial)
            except Exception as e:
                flash('Error al convertir el ID del historial clínico')
                return redirect(url_for('paciente'))

            # Buscar el historial clínico por su _id en la base de datos
            historial_clinico = db.get_collection('historial_clinico').find_one({'_id': id_historial})
            
            # Actualizar los campos de antecedentes médicos con los nuevos valores
            historial_clinico['antecedentes_medicos']['enfermedades_cronicas'] = enfermedadesCronicas
            historial_clinico['antecedentes_medicos']['alergias'] = alergias
            historial_clinico['antecedentes_medicos']['cirugias_previas'] = cirugiasPrevias
            historial_clinico['antecedentes_medicos']['traumatismos_o_lesiones'] = traumatismosLesiones

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
