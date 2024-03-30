from .Models import User,LogGeneral,UsuarioBloqueado
from sqlalchemy import text,desc
import datetime

class UserDAO:

    @classmethod
    def login(cls, user):
        try:

            username = user.nombre_usuario
            password = user.contrasenia
            print(username)
            print(password)
            
            user_from_db = User.query.filter_by(nombre_usuario=username).first()
            if user_from_db and User.check_password(user_from_db.contrasenia, password):
                return user_from_db
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(cls, id_usuario):
        try:
            return User.query.get(id_usuario)
        except Exception as ex:
            raise Exception(ex)

    @staticmethod
    def get_with_permissions(user_id, db):
        # Realiza la consulta para obtener los permisos del usuario
        query = text("""
            SELECT pp.id_permiso AS permisosModulo 
            FROM proyectGalleta.usuario u 
            JOIN proyectGalleta.rol r ON r.id_rol = u.rol
            JOIN proyectGalleta.permiso_rol p ON p.id_rol = r.id_rol
            JOIN proyectGalleta.permiso pp ON pp.id_permiso = p.id_permiso
            WHERE u.id_usuario = :user_id
        """)
        # Ejecuta la consulta 
        result = db.session.execute(query, {'user_id': user_id})        
        # Almacena los permisos en una lista
        lstPermisos = [row.permisosModulo for row in result]
        
        return lstPermisos

    @classmethod
    def get_password_by_username(cls, username):
        # Validar que el nombre de usuario no esté vacío
        if not username:
            return None
        user_from_db = User.query.filter_by(nombre_usuario=username).first()
        if user_from_db:
            return user_from_db.contrasenia
        else:
            return None
    
    def get_fecha_password(user_id,db):
        if not user_id:
            return None
        userDB = User.query.filter_by(id_usuario=user_id).first()
        return userDB.fecha_password if userDB else None

    def actualizar_contrasenia(user_id, nueva_contrasenia, db):
        if not user_id:
            return False

        user = User.query.filter_by(id_usuario=user_id).first()
        if user:
            user.contrasenia = nueva_contrasenia
            user.fecha_password = datetime.datetime.now()
            db.session.commit()
            return True
        else:
            return False
        
    def obtenerId_byNombre(username,db):
        if not username:
            return None
        userDB = User.query.filter_by(nombre_usuario=username).first()
        return userDB.id_usuario if userDB else None
    
    def insertar_log(id_usuario, descripcion, estatus, db):
        try:
            nuevo_log = LogGeneral(
                id_usuario=id_usuario,
                fecha_hora=datetime.datetime.now(),
                descripcion=descripcion,
                estatus=estatus
            )            
            db.session.add(nuevo_log)
            db.session.commit()
            return True
        except Exception as e:
            print("Error al insertar el log:", e)
            return False
        
    def contar_logs(id_usuario, descripcion, estatus, db):
        try:
            fecha_actual = datetime.datetime.now().date()
            contador = LogGeneral.query.filter(
                LogGeneral.id_usuario == id_usuario,
                LogGeneral.descripcion == descripcion,
                LogGeneral.estatus == estatus,
                db.func.DATE(LogGeneral.fecha_hora) == fecha_actual
            ).count()
            return contador
        except Exception as e:
            print("Error al contar los logs:", e)
            return -1
        
    def existeUsuarioBloqueado(id_usuario, db):
        try:
            usuario_bloqueado = UsuarioBloqueado.query.filter_by(id_usuario=id_usuario).first()
            return usuario_bloqueado is not None
        except Exception as e:
            print("Error al verificar el estado del usuario bloqueado:", e)
            return False
    def insertarUsuarioBloqueado(id_usuario, db):
        try:
            nuevo_usuario_bloqueado = UsuarioBloqueado(
                id_usuario=id_usuario,
                fecha=datetime.datetime.now()
            )            
            db.session.add(nuevo_usuario_bloqueado)
            db.session.commit()
            return True
        except Exception as e:
            print("Error al insertar el usuario bloqueado:", e)
            return False
        
    def obtenerUltimoInicioSesionExitoso(id_usuario, db):
        try:
            datosInicioSesion = LogGeneral.query.filter_by(id_usuario=id_usuario, descripcion='Inicio de sesión exitoso', estatus=1)\
                .order_by(desc(LogGeneral.fecha_hora)).first()
            if datosInicioSesion:
                return datosInicioSesion.fecha_hora
            else:
                return None
        except Exception as e:
            print("Error al obtener el último inicio de sesión exitoso:", e)
            return None
        
    def obtenerUltimoInicioSesionExitosoAnterior(id_usuario, db):
        try:
            segundoInicioSesion = LogGeneral.query.filter_by(id_usuario=id_usuario, descripcion='Inicio de sesión exitoso', estatus=1)\
                .order_by(desc(LogGeneral.fecha_hora)).offset(1).first()
            if segundoInicioSesion:
                return segundoInicioSesion.fecha_hora
            else:
                return None
        except Exception as e:
            print("Error al obtener el segundo inicio de sesión exitoso:", e)
            return None