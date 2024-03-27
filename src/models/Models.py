from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'usuario'  # Nombre de la tabla en la base de datos

    id_usuario = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(100), nullable=False, unique=True)
    contrasenia = db.Column(db.String(500), nullable=False)
    rol = db.Column(db.SmallInteger, nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    fecha_password = db.Column(db.DateTime, default=datetime.datetime.now)
    def get_id(self):
        return str(self.id_usuario)

    @classmethod
    def check_password(self, hashed_password, contrasenia):
        return check_password_hash(hashed_password, contrasenia)

class Rol(db.Model):
    __tablename__ = 'rol'
    
    id_rol = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)