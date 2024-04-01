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

class Galleta(db.Model):
    __tablename__ = 'galleta'

    id_galleta = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    porcentaje_ganacia = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.Text)

    def __init__(self, nombre, porcentaje_ganacia, imagen=None):
        self.nombre = nombre
        self.porcentaje_ganacia = porcentaje_ganacia
        self.imagen = imagen

class MateriaPrima(db.Model):
    __tablename__ = 'materia_prima'

    id_materia = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    costo = db.Column(db.Float, nullable=True)

    def __init__(self, nombre, costo=None):
        self.nombre = nombre
        self.costo = costo

class Receta(db.Model):
    __tablename__ = 'receta'

    id_receta = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre_receta = db.Column(db.String(100), nullable=False)
    id_galleta = db.Column(db.SmallInteger, db.ForeignKey('galleta.id_galleta'), nullable=False)

    galleta = db.relationship('Galleta', backref=db.backref('recetas', lazy=True))

class RecetaMateriaIntermedia(db.Model):
    __tablename__ = 'receta_materia_intermedia'

    id_receta_producto_terminado = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.SmallInteger, db.ForeignKey('receta.id_receta'), nullable=False)
    id_materia = db.Column(db.SmallInteger, db.ForeignKey('materia_prima.id_materia'), nullable=False)
    cantidad = db.Column(db.Float, nullable=True)

    receta = db.relationship('Receta', backref=db.backref('materias_intermedias', lazy=True))
    materia_prima = db.relationship('MateriaPrima', backref=db.backref('recetas_intermedias', lazy=True))

class Equivalencia(db.Model):
    __tablename__ = 'equivalencia'

    id_equivalencia = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.SmallInteger, db.ForeignKey('receta.id_receta'), nullable=False)
    piezas = db.Column(db.Integer, nullable=False)
    gramaje = db.Column(db.Float, nullable=False)

    receta = db.relationship('Receta', backref=db.backref('equivalencias', lazy=True))