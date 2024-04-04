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

class Venta(db.Model):
    __tablename__ = 'venta'
    
    id_venta = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    fecha_venta = db.Column(db.DateTime, nullable=False)
    hora_venta = db.Column(db.Time, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    
    id_detalle_venta = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_venta = db.Column(db.SmallInteger, db.ForeignKey('venta.id_venta'), nullable=False)
    id_galleta = db.Column(db.SmallInteger, nullable=False)
    medida = db.Column(db.String(20), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

    venta = db.relationship('Venta', backref=db.backref('detalles_venta', lazy=True))

class InventarioProductoTerminado(db.Model):
    __tablename__ = 'inventario_producto_terminado'

    id_inventario_prod_terminado = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_galleta = db.Column(db.SmallInteger, db.ForeignKey('galleta.id_galleta'), nullable=False)
    fecha_produccion = db.Column(db.DateTime, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    estatus = db.Column(db.Integer, default=None)

    galleta = db.relationship('Galleta', backref=db.backref('inventario_producto_terminado', lazy=True))

    def __init__(self, id_galleta, fecha_produccion, cantidad, estatus=None):
        self.id_galleta = id_galleta
        self.fecha_produccion = fecha_produccion
        self.cantidad = cantidad
        self.estatus = estatus