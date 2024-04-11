from flask import url_for, redirect, session, request, flash
import database as dbase
from bson.objectid import ObjectId


db = dbase.dbConnection()
def init_usuario_delete(app):
    
#ELIMINAR
    @app.route('/eliminar_resultado_laboratorio/<id_historial>', methods=['POST'])
    def eliminar_resultado_laboratorio(id_historial):
        if 'correo' in session:
            indice = int(request.form.get('indice'))

            try:
                # Convertir id_historial a ObjectId
                id_historial = ObjectId(id_historial)
            except Exception as e:
                flash('Error al convertir el ID del historial clínico')
                return redirect(url_for('paciente'))

            # Buscar el historial clínico por su _id en la base de datos
            historial_clinico = db.get_collection('historial_clinico').find_one({'_id': id_historial})

            if historial_clinico:
                if 'examenes_pruebas_medicas' in historial_clinico and 'resultados_laboratorio' in historial_clinico['examenes_pruebas_medicas']:
                    # Verificar si el índice está dentro de los límites de la lista
                    if 0 <= indice < len(historial_clinico['examenes_pruebas_medicas']['resultados_laboratorio']):
                        # Eliminar el resultado de laboratorio en el índice especificado
                        historial_clinico['examenes_pruebas_medicas']['resultados_laboratorio'].pop(indice)

                        # Actualizar el historial clínico en la base de datos
                        result = db.get_collection('historial_clinico').update_one(
                            {'_id': id_historial},
                            {'$set': historial_clinico}
                        )
                        flash('Resultado de laboratorio eliminado exitosamente')
                    else:
                        flash('Índice de resultado de laboratorio fuera de rango')
                else:
                    flash('No hay resultados de laboratorio para eliminar')
            else:
                flash('Historial clínico no encontrado en la base de datos')
        else:
            flash('Usuario no ha iniciado sesión')

        return redirect(url_for('mi_historial'))
