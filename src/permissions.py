from functools import wraps
from flask import abort
from flask_login import current_user
from models.usersDao import UserDAO
from models.Models import db

def permission_required(permission_id):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # Verificar si el usuario está autenticado
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            

            print("Permiso Parametro .................... {}".format(permission_id))
            
            permissions = UserDAO.get_with_permissions(current_user.id_usuario,db)
            current_user.permisos = permissions

            print("Permisos Usuario .................... {}".format(current_user.permisos))

            if permission_id not in current_user.permisos:
                abort(403)   # Devuelve un error HTTP 403 Forbidden si el usuario no tiene el permiso
                # Puedes personalizar el mensaje de error según tus necesidades

            return func(*args, **kwargs)
        return decorated_function
    return decorator
