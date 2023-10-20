import datetime
from inspect import indentsize
import json
import os
import sys
import secrets
from flask import Flask, request, jsonify, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS 
from supabase import create_client
from chatbot import get_response, predict_class
# Crear una instancia de la aplicación Flask
app = Flask(__name__)
CORS(app) # Aplica CORS a la aplicación
# Configurar la clave secreta de la aplicación y la clave secreta para JWT
app.secret_key = secrets.token_urlsafe(32)
app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(32)

# Configurar el sistema de gestión de tokens JWT
jwt = JWTManager(app)

# Configuración de las credenciales de Supabase
SUPABASE_URL = "https://nrnbqoxuhupcxlboisyg.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ybmJxb3h1aHVwY3hsYm9pc3lnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5NzM4MzI5MCwiZXhwIjoyMDEyOTU5MjkwfQ.YkFTxwAKzNs6gukWMOA9ug6sboUJgEVU_SWJQmtzawU" 
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)


# Ruta para obtener los datos de intents.json para el chatbot
intents = json.loads(open('intents.json', encoding='utf-8').read())

# Ruta para obtener la lista de usuarios
@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        response = supabase.table("usuarios").select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)})
    
# Ruta para obtener un usuario por su ID
@app.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
def obtener_usuario_por_id(usuario_id):
    try:
        response = supabase.table("usuarios").select("*").eq('id', usuario_id).execute()
        if response.data:
            # Si se encuentra el usuario, retornar sus datos
            return jsonify(response.data[0])
        else:
            # Si no se encuentra el usuario, retornar un mensaje de error
            return jsonify({"mensaje": "Usuario no encontrado"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Ruta para registrar un nuevo usuario
@app.route('/api/usuarios', methods=['POST'])
def registrar_usuario():
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        email = data.get('email')
        contraseña = data.get('contraseña')

        # Registrarse en el servicio de autenticación de Supabase
        response = supabase.auth.sign_up({"email": email, "password": contraseña})

        # Crear un nuevo usuario y almacenarlo en la base de datos
        nuevo_usuario = {
            "nombre": nombre,
            "email": email,
            "contraseña": contraseña,
            "es_administrador": False,
        }
        supabase.table("usuarios").upsert([nuevo_usuario]).execute()

        return jsonify({"mensaje": "Usuario registrado con éxito"})
    except Exception as e:
        return jsonify({"error": str(e)})
    

# Ruta para registrar un nuevo usuario Adnin
@app.route('/api/usuariosadmin', methods=['POST'])
def registrar_usuarioadmin():
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        email = data.get('email')
        contraseña = data.get('contraseña')

        # Registrarse en el servicio de autenticación de Supabase
        response = supabase.auth.sign_up({"email": email, "password": contraseña})

        # Crear un nuevo usuario y almacenarlo en la base de datos
        nuevo_usuario = {
            "nombre": nombre,
            "email": email,
            "contraseña": contraseña,
            "es_administrador": True,
        }
        supabase.table("usuarios").upsert([nuevo_usuario]).execute()

        return jsonify({"mensaje": "Usuario Admin registrado con éxito"})
    except Exception as e:
        return jsonify({"error": str(e)})
    
    

# Ruta para actualizar un usuario por su ID
@app.route('/api/usuarios/<int:usuario_id>', methods=['PUT'])
@jwt_required()
def actualizar_usuario_por_id(usuario_id):
    try:
        # Verificar si el usuario existe
        existe_usuario = supabase.table("usuarios").select("*").eq('id', usuario_id).execute().data

        if not existe_usuario:
            return jsonify({"mensaje": "Usuario no encontrado"})

        # Obtener los datos actualizados del usuario desde la solicitud
        datos_actualizados = request.get_json()

        # Filtrar solo los campos permitidos para la actualización
        campos_permitidos = ["nombre", "email", "contraseña"]
        datos_actualizados = {campo: datos_actualizados[campo] for campo in campos_permitidos if campo in datos_actualizados}

        # Actualizar el usuario en la base de datos
        supabase.table("usuarios").update(datos_actualizados).eq("id", usuario_id).execute()

        return jsonify({"mensaje": "Usuario actualizado con éxito"})
    except Exception as e:
        return jsonify({"error": str(e)})
    
# Ruta para eliminar un usuario por su ID
@app.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
@jwt_required()
def eliminar_usuario_por_id(usuario_id):
    try:
        # Verificar si el usuario existe
        existe_usuario = supabase.table("usuarios").select("*").eq('id', usuario_id).execute().data

        if not existe_usuario:
            return jsonify({"mensaje": "Usuario no encontrado"})

        # Eliminar el usuario en la base de datos
        supabase.table("usuarios").delete().eq("id", usuario_id).execute()

        return jsonify({"mensaje": "Usuario eliminado con éxito"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Ruta para iniciar sesión y obtener un token JWT
@app.route('/api/iniciar_sesion', methods=['POST'])
def iniciar_sesion():
    try:
        data = request.get_json()
        email = data.get('email')
        contraseña = data.get('password')

        # Autenticar al usuario utilizando el servicio de autenticación de Supabase
        supabase.auth.sign_in_with_password({"email": email, "password": contraseña})

        # Obtener la información del usuario, incluyendo el nombre y el ID
        usuario_info = supabase.table("usuarios").select("id", "nombre", "es_administrador").match({'email': email}).execute()
        usuario_data = usuario_info.data[0] if usuario_info.data else None

        # Crear un token JWT para el usuario autenticado y darle tiempo de expiración a 1 hora
        access_token = create_access_token(identity=email, expires_delta=datetime.timedelta(seconds=3600))

        # Almacenar el token en la variable de sesión (opcional)
        session['access_token'] = access_token

        return jsonify({
            "mensaje": "Usuario autenticado con éxito",
            "access_token": access_token,
            "id_usuario": usuario_data['id'] if usuario_data else None,
            "nombre_usuario": usuario_data['nombre'] if usuario_data else None,
            "es_administrador": usuario_data['es_administrador'] if usuario_data else None
        })
    except Exception as e:
        return jsonify({"error": str(e)})
    
# Ruta para cerrar sesión (requiere autenticación)
@app.route('/api/cerrar_sesion', methods=['GET'])
@jwt_required()
def cerrar_sesion():
    try:
        # Cerrar sesión utilizando el servicio de autenticación de Supabase
        supabase.auth.sign_out()
        return jsonify({"mensaje": "Usuario desconectado"})
    except Exception as e:
        return jsonify({"error": str(e)})
    
# Ruta para consultar el historial de chat (requiere autenticación)
@app.route('/api/historial_chat', methods=['GET'])
@jwt_required()
def consultar_historial():
    try:
        response = supabase.table("historial_chat").select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)})
    
# Ruta para consultar el historial de chat por su ID (requiere autenticación)
@app.route('/api/historial_chat/<int:usuario_id>', methods=['GET'])
@jwt_required()
def consultar_historial_por_id(usuario_id):
    try:
        response = supabase.table("historial_chat").select("*").eq('usuario_id', usuario_id).execute()
        if response.data:
            # Si se encuentra el usuario, retornar sus datos
            return jsonify(response.data)
        else:
            # Si no se encuentra el usuario, retornar un mensaje de error
            return jsonify({"mensaje": "Usuario no encontrado"})
    except Exception as e:
        return jsonify({"error": str(e)})

    
# Ruta para procesar solicitudes del chatbot (requiere autenticación)
@app.route('/api/chat', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json()
    message = data.get('message', '')
    
    # Utilizar el chatbot para obtener una respuesta
    ints = predict_class(message)
    res = get_response(ints, intents)
    
    try:
        mensaje = message
        respuesta_chatbot = res

        # Obtener el ID del usuario utilizando el correo electrónico de la sesión
        email = get_jwt_identity()
        lista = supabase.table("usuarios").select("*").match({'email': email}).execute()
        usuario_id = lista.data[0]['id']

        # Insertar en la tabla historial_chat
        supabase.table("historial_chat").upsert([
            {
                "usuario_id": usuario_id,
                "mensaje": mensaje,
                "respuesta_chatbot": respuesta_chatbot
            }
        ]).execute()

        return jsonify({"response": res, "mensaje": "Historial de chat guardado con éxito"})
    except Exception as e:
        return jsonify({"response": res, "error": str(e)})
    

# Ruta para obtener la lista de contactos
@app.route('/api/contactos', methods=['GET'])
def obtener_contactos():
    try:
        response = supabase.table("contactos").select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)})
    
# Ruta para obtener un contacto por su ID
@app.route('/api/contactos/<int:usuario_id>', methods=['GET'])
def obtener_contacto_por_id(usuario_id):
    try:
        response = supabase.table("contactos").select("*").eq('usuario_id', usuario_id).execute()
        if response.data:
            # Si se encuentra el usuario, retornar sus datos
            return jsonify(response.data)
        else:
            # Si no se encuentra el usuario, retornar un mensaje de error
            return jsonify({"mensaje": "Contactos no encontrados"})
    except Exception as e:
        return jsonify({"error": str(e)})
    
# Ruta para insertar un nuevo contacto
@app.route('/api/contactos', methods=['POST'])
@jwt_required()
def insertar_contacto():
    try:
        data = request.get_json()

        # Obtener los datos del formulario o solicitud
        mensaje = data.get('mensaje')

        # Obtener el ID del usuario utilizando el correo electrónico de la sesión
        email = get_jwt_identity()
        lista = supabase.table("usuarios").select("*").match({'email': email}).execute()
        usuario_id = lista.data[0]['id']

        # Insertar en la tabla contactos 
        supabase.table("contactos").upsert([
            {
                "usuario_id": usuario_id,
                "mensaje": mensaje
            }
        ]).execute()

        return jsonify({"mensaje": "Contacto registrado con éxito"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Iniciar la aplicación si este script es ejecutado directamente
if __name__ == "__main__":
    app.run(debug=True)