from werkzeug.security import check_password_hash
from flask_login import UserMixin


class Usuario(UserMixin):

    def __init__(self, id_usuario, nombre_usuario, contrasenia,rol="",nombre_completo="",fecha_password="") -> None:
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario
        self.contrasenia = contrasenia
        self.rol = rol
        self.nombre_completo = nombre_completo
        self.fecha_password = fecha_password

    @classmethod
    def check_password(self, hashed_password, contrasenia):
        return check_password_hash(hashed_password, contrasenia)
