### REQUERIMIENTOS

Para utilizar esta API, asegúrate de cumplir con los siguientes requerimientos:

1. **Python 3.9:** Se recomienda utilizar Python 3.9, ya que la API ha sido desarrollada en esta versión.

2. **Instalación de dependencias:** Ejecuta el siguiente comando para instalar todas las dependencias necesarias listadas en el archivo `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

3. **Ejecución del entrenamiento:** Ejecuta el script `training.py`. Este paso es necesario ya que se instalan algunos archivos localmente en la máquina a través de la librería TensorFlow para las redes neuronales del chatbot.

4. **Ejecución de la API:** Para iniciar la API, ejecuta el script `api.py`. Una vez ejecutado, puedes realizar peticiones a la API según sea necesario.

## Nota Importante

Para acceder a las rutas que requieren autenticación, sigue estos pasos:

1. Inicia sesión con un usuario registrado para obtener un token de autenticación.

2. Utiliza el token generado durante el inicio de sesión para acceder a las rutas que requieren autenticación.

3. Incluye el token en el encabezado de la solicitud de la siguiente manera:

    - **Key (Clave):** `Authorization`
    - **Value (Valor):** `Bearer tokengeneradoaliniciarseccion`

Este proceso garantiza que solo los usuarios autenticados y autorizados tengan acceso a las funciones protegidas de la aplicación, proporcionando un nivel adicional de seguridad y control en el manejo de datos y recursos.

# Rutas relacionadas con Usuarios

## Obtener todos los usuarios
- Ruta: `/api/usuarios`
- Método HTTP: GET
- Descripción: Retorna todos los usuarios registrados.
- Autenticación: No se requiere.

## Obtener un usuario por ID
- Ruta: `/api/usuarios/<int:usuario_id>`
- Método HTTP: GET
- Descripción: Retorna la información de un usuario específico.
- Parámetros de Ruta: `usuario_id` es el identificador único del usuario.
- Autenticación: No se requiere.

## Registrar un nuevo usuario
- Ruta: `/api/usuarios`
- Método HTTP: POST
- Descripción: Registra un nuevo usuario en el sistema.
- Datos de la Solicitud: Nombre, email, y contraseña del nuevo usuario.
- Autenticación: No se requiere.

## Registrar un nuevo usuario Administrador
- Ruta: `/api/usuariosadmin`
- Método HTTP: POST
- Descripción: Registra un nuevo usuario Administrador en el sistema.
- Datos de la Solicitud: Nombre, email, y contraseña del nuevo usuario.
- Autenticación: No se requiere.

## Actualizar un usuario por ID
- Ruta: `/api/usuarios/<int:usuario_id>`
- Método HTTP: PUT
- Descripción: Actualiza la información de un usuario específico.
- Parámetros de Ruta: `usuario_id` es el identificador único del usuario.
- Datos de la Solicitud: Los campos a actualizar (nombre, email, contraseña).
- Autenticación: Se requiere un token JWT.

## Eliminar un usuario por ID
- Ruta: `/api/usuarios/<int:usuario_id>`
- Método HTTP: DELETE
- Descripción: Elimina un usuario específico del sistema.
- Parámetros de Ruta: `usuario_id` es el identificador único del usuario.
- Autenticación: Se requiere un token JWT.

## Iniciar Sesión
- Ruta: `/api/iniciar_sesion`
- Método HTTP: POST
- Descripción: Autentica al usuario y proporciona un token JWT.
- Datos de la Solicitud: Email y contraseña del usuario.
- Autenticación: No se requiere.

## Cerrar Sesión
- Ruta: `/api/cerrar_sesion`
- Método HTTP: GET
- Descripción: Cierra la sesión actual del usuario.
- Autenticación: Se requiere un token JWT.

# Rutas relacionadas con Historial de Chat

## Obtener historial de chat
- Ruta: `/api/historial_chat`
- Método HTTP: GET
- Descripción: Retorna el historial completo de chat.
- Autenticación: Se requiere un token JWT.

## Obtener historial de chat por ID de Usuario
- Ruta: `/api/historial_chat/<int:usuario_id>`
- Método HTTP: GET
- Descripción: Retorna el historial de chat de un usuario específico.
- Parámetros de Ruta: `usuario_id` es el identificador único del usuario.
- Autenticación: Se requiere un token JWT.

# Rutas relacionadas con Chat

## Procesar solicitudes del chatbot (requiere autenticación)
- Ruta: `/api/chat`
- Método HTTP: POST
- Descripción: Procesa las solicitudes del chatbot y guarda el historial de chat.
- Autenticación: Se requiere un token JWT.

### Datos de la Solicitud:
- Datos JSON con el siguiente formato:
  ```json
  {
    "message": "Texto del mensaje"
  }

# Rutas relacionadas con Contactos

## Obtener todos los contactos
- Ruta: `/api/contactos`
- Método HTTP: GET
- Descripción: Retorna todos los contactos registrados.
- Autenticación: No se requiere.

## Obtener contacto por ID de Usuario
- Ruta: `/api/contactos/<int:usuario_id>`
- Método HTTP: GET
- Descripción: Retorna los contactos de un usuario específico.
- Parámetros de Ruta: `usuario_id` es el identificador único del usuario.
- Autenticación: No se requiere.

## Insertar nuevo contacto
- Ruta: `/api/contactos`
- Método HTTP: POST
- Descripción: Registra un nuevo contacto.
- Datos de la Solicitud: Mensaje del contacto.
- Autenticación: Se requiere un token JWT.
