import functools
from flask import make_response, session, Response
import database as dbase
db = dbase.dbConnection()
import random
import string


#FUNCIONES
def obtener_historial_clinico(usuario_id):
    historial_clinico = db['historial_clinico'].find_one({'usuario_id': usuario_id})
    return historial_clinico

def obtener_usuario(correo):
    usuario = db['pacientes'].find_one({'correo': correo})
    return usuario

def obtener_doctor(correo):
    usuario = db['doctor'].find_one({'correo': correo})
    return usuario

def obtener_usuario_por_numero_social(numero_social):
    usuario = db['pacientes'].find_one({'numeroSocial': numero_social})
    return usuario

def generar_captcha():
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    session['captcha'] = captcha_text
    return captcha_text

def nocache(view):
    @functools.wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return no_cache