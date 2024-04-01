from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_login import UserMixin
import datetime
from sqlalchemy.orm import relationship

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
    #Permite relacionar con el modelo rol
    roles = db.relationship('PermisoRol',backref='rol',lazy='dynamic')
    def __repr__(self):
        return '<Rol %r>' % (self.nombre)
    
class Permiso(db.Model):
    __tablename__ = 'permiso'

    id_permiso = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    permiso = db.Column(db.String(100), nullable=False)

    permisos = db.relationship('PermisoRol',backref='permiso',lazy='dynamic')
    def __repr__(self):
        return '<Permiso %r>' % (self.permiso)

class PermisoRol(db.Model):
    __tablename__ = 'permiso_rol'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_rol = db.Column(db.SmallInteger, db.ForeignKey('rol.id_rol'), nullable=False)
    id_permiso = db.Column(db.SmallInteger, db.ForeignKey('permiso.id_permiso'), nullable=False)
    
class Proveedor(db.Model):
    __tablename__ = 'proveedor'

    id_proveedor = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(200), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(50), nullable=False)
    nombre_responsable = db.Column(db.String(200), nullable=False)

class LogGeneral(db.Model):
    __tablename__ = 'logs_general'

    id_log = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.SmallInteger, nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    descripcion = db.Column(db.String(250), nullable=False)
    estatus = db.Column(db.SmallInteger, default=None)

class UsuarioBloqueado(db.Model):
    __tablename__ = 'usuarios_bloqueados'

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.SmallInteger)
    fecha = db.Column(db.DateTime)


class Compra(db.Model):
    __tablename__ = 'compras'

    id = db.Column(db.Integer, primary_key=True)
    nombre_producto = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_compra = db.Column(db.Float, nullable=False)
    fecha_compra = db.Column(db.Date, nullable=False)
    fecha_caducidad = db.Column(db.Date, nullable=False)
    nombre_proveedor = db.Column(db.String(200), nullable=False)

class Galleta(db.Model):
    __tablename__ = 'galleta'

    id_galleta = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    porcentaje_ganancia = db.Column(db.Double, nullable=False)
    imagen = db.Column(db.Text, default=None, nullable=True)
    inventarios = relationship('InventarioProductoTerminado', backref='galleta')
    recetas = relationship('Receta', backref='galleta')

    def __repr__(self) -> str:
       return f'{self.nombre}'

class InventarioProductoTerminado(db.Model):
    __tablename__ = 'inventario_producto_terminado'

    id_inventario_prod_terminado = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_galleta = db.Column(db.SmallInteger, db.ForeignKey('galleta.id_galleta'), nullable=False)
    fecha_produccion = db.Column(db.DateTime, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    estatus = db.Column(db.SmallInteger)

    mermas = relationship("MermaProdTerminado", back_populates="inventario_prod_terminado")

class MermaProdTerminado(db.Model):
    __tablename__ = 'merma_prod_terminado'

    id_merma_prod_terminado = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_inventario_prod_terminado = db.Column(db.SmallInteger, db.ForeignKey('inventario_producto_terminado.id_inventario_prod_terminado'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime)

    # Definir la relación inversa
    inventario_prod_terminado = relationship("InventarioProductoTerminado", back_populates="mermas")

class SolicitudProduccion(db.Model):
    __tablename__ = 'solicitud_prooduccion'

    id_solicitud = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.SmallInteger, db.ForeignKey('receta.id_receta'), nullable=False)
    fecha_solicitud = db.Column(db.DateTime)
    id_usuario = db.Column(db.SmallInteger, nullable=False)
    fecha_terminacion = db.Column(db.DateTime)
    estatus = db.Column(db.String(100))
    receta = db.relationship('Receta', backref='solicitudes')

class Receta(db.Model):
    __tablename__ = 'receta'

    id_receta = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre_receta = db.Column(db.String(100), nullable=False)
    id_galleta = db.Column(db.SmallInteger, db.ForeignKey('galleta.id_galleta'), nullable=False)
    # Relación de uno a uno con Equivalencia
    equivalencias = db.relationship("Equivalencia", backref="recetas", uselist=False, cascade="all, delete-orphan")
    galletas = db.relationship("Galleta",  backref="recetas_galleta")
    materias = db.relationship("MateriaPrima", secondary='receta_materia_intermedia', back_populates='recetas')
    #receta_materia_intermedia = db.relationship("RecetaMateriaIntermedia",  backref='recetas_materias')

    def __repr__(self) -> str:
       return f'{self.nombre_receta}'

class Equivalencia(db.Model):
    __tablename__ = 'equivalencia'

    id_equivalencia = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.SmallInteger, db.ForeignKey('receta.id_receta'), nullable=False)
    piezas = db.Column(db.Integer, nullable=False)
    gramaje = db.Column(db.Double, nullable=False)

    #recetas= db.relationship("Receta", back_populates="equivalencias")

    def __repr__(self) -> str:
       return f'{self.gramaje} gr - {self.piezas} pz'

class RecetaMateriaIntermedia(db.Model):
    __tablename__ = 'receta_materia_intermedia'

    id_receta_producto_terminado = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_receta = db.Column(db.SmallInteger, db.ForeignKey('receta.id_receta'), nullable=False)
    id_materia = db.Column(db.SmallInteger, db.ForeignKey('materia_prima.id_materia'), nullable=False)
    cantidad = db.Column(db.Float)

class MateriaPrima(db.Model):
    __tablename__ = 'materia_prima'

    id_materia = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    costo = db.Column(db.Double)
    # Relación de muchos a muchos con Receta a través de RecetaMateriaIntermedia
    recetas = db.relationship("Receta", secondary='receta_materia_intermedia', back_populates='materias')

    def __repr__(self) -> str:
       return f'{self.nombre}'
    
    def get_cantidad_en_receta(self, receta_id):
        receta_materia = RecetaMateriaIntermedia.query.filter_by(id_materia=self.id_materia, id_receta=receta_id).first()
        if receta_materia:
            return receta_materia.cantidad
        return 0  # Si no hay cantidad especificada en la tabla intermedia, retornar 0 o cualquier otro valor predeterminado

class Inventario(db.Model):
    __tablename__ = 'inventario'

    id_inventario = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_materia = db.Column(db.SmallInteger, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_caducidad = db.Column(db.DateTime, nullable=False)
    estatus = db.Column(db.SmallInteger, nullable=False)
    id_proveedor = db.Column(db.SmallInteger, nullable=False)

    
