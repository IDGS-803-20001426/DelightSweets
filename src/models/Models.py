from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_login import UserMixin
import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey  
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
    inventariosMateria = relationship('Inventario', backref='proveedor')

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
    porcentaje_ganancia = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.Text)
    inventarios = relationship('InventarioProductoTerminado', backref='galleta')
    recetas = relationship('Receta', backref='galleta')  # Elimina este backref

    def __repr__(self) -> str:
       return f'{self.nombre}'

    def __init__(self, nombre, porcentaje_ganancia, imagen=None):
        self.nombre = nombre
        self.porcentaje_ganancia = porcentaje_ganancia
        self.imagen = imagen

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

    # receta = db.relationship('Receta', backref=db.backref('equivalencias', lazy=True))

    def __repr__(self) -> str:
       return f'{self.gramaje} gr - {self.piezas} pz'

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
    id_galleta = db.Column(Integer, ForeignKey('galleta.id_galleta'), nullable=False)
    medida = db.Column(db.String(20), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

    venta = db.relationship('Venta', backref=db.backref('detalles_venta', lazy=True))
    galleta = relationship('Galleta')

class InventarioProductoTerminado(db.Model):
    __tablename__ = 'inventario_producto_terminado'

    id_inventario_prod_terminado = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_galleta = db.Column(db.SmallInteger, db.ForeignKey('galleta.id_galleta'), nullable=False)
    fecha_produccion = db.Column(db.DateTime, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    estatus = db.Column(db.Integer, default=None)

    galleta_relacionada = db.relationship('Galleta', backref=db.backref('inventarios_producto_terminado', lazy=True))
    mermas = relationship("MermaProdTerminado", back_populates="inventario_prod_terminado")

    
    def __init__(self, id_galleta, fecha_produccion, cantidad, estatus=None):
        self.id_galleta = id_galleta
        self.fecha_produccion = fecha_produccion
        self.cantidad = cantidad
        self.estatus = estatus

class MermaProdTerminado(db.Model):
    __tablename__ = 'merma_prod_terminado'

    id_merma_prod_terminado = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_inventario_prod_terminado = db.Column(db.SmallInteger, db.ForeignKey('inventario_producto_terminado.id_inventario_prod_terminado'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime)
    motivo = db.Column(db.String(250), nullable=False)

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
    equivalencias = db.relationship("Equivalencia", backref="receta", uselist=False, cascade="all, delete-orphan")
    galletas = db.relationship("Galleta", backref="recetas_galleta")
    materias = db.relationship("MateriaPrima", secondary='receta_materia_intermedia', back_populates='recetas')
    # Elimina este backref para resolver el conflicto
    # galleta = db.relationship('Galleta', backref=db.backref('recetas', lazy=True))

    def __repr__(self) -> str:
       return f'{self.nombre_receta}'


class MateriaPrima(db.Model):
    __tablename__ = 'materia_prima'

    id_materia = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    costo = db.Column(db.Float, nullable=True)
    # Relación de muchos a muchos con Receta a través de RecetaMateriaIntermedia
    recetas = db.relationship("Receta", secondary='receta_materia_intermedia', back_populates='materias')
    inventariosMateria = relationship('Inventario', backref='materia_prima')
    merma_produccion = relationship('MermaProduccion', backref='materia_prima')

    def __init__(self, nombre, costo=None):
        self.nombre = nombre
        self.costo = costo
    
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
    id_materia = db.Column(db.SmallInteger, db.ForeignKey('materia_prima.id_materia'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_caducidad = db.Column(db.DateTime, nullable=False)
    estatus = db.Column(db.SmallInteger, nullable=False)
    id_proveedor = db.Column(db.SmallInteger, db.ForeignKey('proveedor.id_proveedor'), nullable=False)

class MermaProduccion(db.Model):
    __tablename__ = 'merma_produccion'

    id_merma_produccion = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_materia = db.Column(db.SmallInteger, db.ForeignKey('materia_prima.id_materia'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.String(250), nullable=False)

class CorteCaja(db.Model):
    __tablename__ = 'corte_caja'

    id_corte_caja = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    fecha_de_inicio = db.Column(db.Date, nullable=True)
    hora_inicio = db.Column(db.Time, nullable=True)
    fecha_de_termino = db.Column(db.Date, nullable=True)
    hora_termino = db.Column(db.Time, nullable=True)
    estatus = db.Column(db.SmallInteger, nullable=False)
    id_usuario = db.Column(db.Integer, nullable=False)

    def __init__(self, fecha_de_inicio, hora_inicio, fecha_de_termino, hora_termino, estatus, id_usuario):
        self.fecha_de_inicio = fecha_de_inicio
        self.hora_inicio = hora_inicio
        self.fecha_de_termino = fecha_de_termino
        self.hora_termino = hora_termino
        self.estatus = estatus
        self.id_usuario = id_usuario

class CorteCajaVenta(db.Model):
    __tablename__ = 'corte_caja_venta'

    id_corte_caja_venta = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    id_venta = db.Column(db.SmallInteger, nullable=False)
    id_corte_caja = db.Column(db.SmallInteger, nullable=False)
    estatus = db.Column(db.SmallInteger, nullable=True)

    def __init__(self, id_venta, id_corte_caja, estatus):
        self.id_venta = id_venta
        self.id_corte_caja = id_corte_caja
        self.estatus = estatus

class Retiro(db.Model):
    __tablename__ = 'retiro'

    id_retiro = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    id_corte_caja = db.Column(db.SmallInteger, nullable=False)
    id_usuario = db.Column(db.Integer, nullable=False)

    def __init__(self, fecha_hora, monto, motivo, id_corte_caja, id_usuario):
        self.fecha_hora = fecha_hora
        self.monto = monto
        self.motivo = motivo
        self.id_corte_caja = id_corte_caja
        self.id_usuario = id_usuario
