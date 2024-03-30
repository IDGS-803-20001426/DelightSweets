from flask import Flask, render_template, request, redirect, url_for, flash,jsonify,abort
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required,current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.base import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash,check_password_hash
from wtforms import PasswordField, StringField,SelectField
from wtforms.validators import DataRequired,Regexp
from functools import wraps
from permissions import permission_required
from validaciones import validarPalabrasConsulta,validarFormulario,validarContrasenia,cargarContraseñasComunes,validarCamposLogin
from datetime import datetime, timedelta
import re

# Models:
from models.Models import User,db,PermisoRol, Permiso, Rol,Proveedor,MateriaPrima
from models.entities.User import Usuario
from models.usersDao import UserDAO
from config import DevelopmentConfig



app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf = CSRFProtect()
login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id_usuario):
    return UserDAO.get_by_id(id_usuario)

        
class MyModelView(ModelView):
    list_template = 'admin/list.html'
    base_template = 'layoutMaster.html'
    # @permission_required(1)

    def is_accessible(self):
        if current_user.is_authenticated:
            return True
        return False
        
admin = Admin(
    app,
    name='Panel Administrador',  # Nombre personalizado para el panel de administración
    base_template='layoutMaster.html',  # Plantilla base personalizada
    template_mode='bootstrap3'  # Modo de plantilla 
)

#Clase Usuarios ------------------------------------------------------------------------

class UserView(MyModelView):
    column_exclude_list = ('contrasenia')  # No muestra en la tabla lista
    form_excluded_columns = ('fecha_password')  # Campos Excluidos de los formularios

    @login_required
    def is_accessible(self):
        permiso = 1
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    
    def validate_form(self, form):
        
        # Primero, llama al método validate_form de la superclase para realizar las validaciones predeterminadas.
        if not super().validate_form(form):
            return False
        
        tieneValor = False
        try:
            form_nombre_usuario = form.nombre_usuario.data
            tieneValor = True
        except AttributeError:
            tieneValor = False

        if tieneValor  :
            contraseniaBD = UserDAO.get_password_by_username(form.nombre_usuario.data)
            contraseniaForm = form.contrasenia.data

            if contraseniaBD:
                contrasenias_comunes = cargarContraseñasComunes()
                if contraseniaForm in contrasenias_comunes:
                    form.contrasenia.errors.append("La contraseña ingresada es común.")
                    return False
                if check_password_hash(contraseniaBD, contraseniaForm) and contraseniaBD :
                    # Las contraseñas coinciden -----------------------------------------------------------------------
                    print("Las contraseñas son iguales.")
                    form.contrasenia.errors.append("La nueva contraseña no puede ser igual a la contraseña anterior.")
                    return False

        # Si no se encontraron problemas, devuelve True para indicar que la validación fue exitosa.
        return True
    

    def scaffold_form(self):
        form_class = super(UserView, self).scaffold_form()
        form_class.rol.validators = []
        # Define password con default value para no mostrar contraseña y requerido   
        form_class.rol = SelectField('Rol', choices=[('1', 'Administrador'), ('2', 'Cocinero'), ('3', 'Ventas')], validators=[DataRequired()])
        
        # Validaciones Personalizadas Ataques
        validarFormulario(form_class, ['nombre_usuario','nombre_completo'])
        validarContrasenia(form_class, 'contrasenia')
         
               
        return form_class

    def on_model_change(self, form, model, is_created):

        model.nombre_usuario = form.nombre_usuario.data.upper()
        model.nombre_completo = form.nombre_completo.data.upper()
        model.contrasenia = generate_password_hash(form.data['contrasenia'])
    
    def rol_formatter(view, context, model, name):
        # Define un diccionario para mapear los números de rol a sus nombres correspondientes
        rol_map = {1: 'Administrador', 2: 'Cocinero', 3: 'Ventas'}
        rol_numero = getattr(model, name)
        return rol_map.get(rol_numero, 'Desconocido')
    
    column_formatters = {'rol': rol_formatter} # Define un formateador personalizado para la columna 'rol'
    column_labels = {'rol': 'Rol'} # Etiqueta personalizada para la columna 'rol'   
    column_descriptions = {'rol': 'Nombre del rol'} # Descripción de la columna 'rol'
    column_default_sort = ('id_usuario', True) # Orden predeterminado de la tabla por la columna 'id_usuario' en orden descendente
#Clase Permisos Rol ------------------------------------------------------------------------
class PermisoRolCreateForm(FlaskForm):
    id_rol = SelectField('Rol', choices=[], validators=[DataRequired()])
    id_permiso = SelectField('Permiso', choices=[], validators=[DataRequired()])

class PermisoRolView(ModelView):
    form = PermisoRolCreateForm
    column_formatters = dict(
        rol=lambda v, c, m, p: m.rol.nombre,
        modulo=lambda v, c, m, p: m.permiso.permiso
    )
    column_labels = {
        'rol': 'Rol',
        'modulo': 'Módulo'
    }
    column_list = ('rol', 'modulo')

    def is_accessible(self):
        permiso = 2
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)

    def on_form_prefill(self, form, id):
        form.id_rol.choices = [(str(rol.id_rol), rol.nombre) for rol in Rol.query.all()]
        form.id_permiso.choices = [(str(permiso.id_permiso), permiso.permiso) for permiso in Permiso.query.all()]
    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.id_rol.choices = [(str(rol.id_rol), rol.nombre) for rol in Rol.query.all()]
        form.id_permiso.choices = [(str(permiso.id_permiso), permiso.permiso) for permiso in Permiso.query.all()]
        return form
    
#Clase Proveedores ------------------------------------------------------------------------
class ProveedorView(MyModelView):
    def is_accessible(self):
        permiso = 3
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)

    def scaffold_form(self):
        form_class = super(ProveedorView, self).scaffold_form()
        
        # Agregar validador para el campo 'telefono'
        form_class.telefono = StringField('Teléfono', validators=[ DataRequired(),
            Regexp(r'^\d+$', message="El teléfono debe contener solo números, sin espacios.")])
        
        # Validaciones Personalizadas Ataques
        validarFormulario(form_class, ['nombre','direccion', 'nombre_responsable'])
        
        return form_class
#Clase Permiso ------------------------------------------------------------------------
class PermisoView(MyModelView):
    def is_accessible(self):
        permiso = 2
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    def scaffold_form(self):
        form_class = super(PermisoView, self).scaffold_form()        
        # Validaciones Personalizadas Ataques
        validarFormulario(form_class, ['permiso'])
        return form_class

#Clase Rol ------------------------------------------------------------------------
class RolView(MyModelView):
    def is_accessible(self):
        permiso = 2
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    
    def scaffold_form(self):
        form_class = super(RolView, self).scaffold_form()        
        # Validaciones Personalizadas Ataques
        validarFormulario(form_class, ['nombre'])
        return form_class
#Clase MateriaPrima ------------------------------------------------------------------------
class MateriaPrimaView(MyModelView):
    def is_accessible(self):
        permiso = 5
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    can_edit = False
    can_delete = False
    can_create = False    

    
#### Añadir views to admin --------------------------------------------------------------------------------------
admin.add_view(UserView(User,db.session,name="usuarios"))
admin.add_view(RolView(Rol,db.session,category='Administración Permisos',name="Rol"))
admin.add_view(PermisoView(Permiso,db.session,category='Administración Permisos',name="Permiso"))
admin.add_view(PermisoRolView(PermisoRol,db.session,category='Administración Permisos',name="Permisos-Roles"))
admin.add_view(ProveedorView(Proveedor,db.session,name="Proveedor"))
admin.add_view(MateriaPrimaView(MateriaPrima,db.session,name="Materia Prima"))





@app.route('/admin')
@login_required 
def admin_panel():
    if current_user.is_authenticated:
        return redirect('/admin/')
    else:
        return redirect(url_for('login'))



@app.route('/protected')
@login_required
@permission_required(4)
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"

#Rutas login & Home ----------------------------------------------------------------------------------------
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # print(request.form['username'])
        # print(request.form['password'])
        if not validarCamposLogin(request.form['username'], request.form['password']):
            flash("Los valores ingresados no son validos")
            return render_template('auth/login.html')
        nombreUsuario = request.form['username']
        user = Usuario(0, request.form['username'], request.form['password'])
        logged_user = UserDAO.login(user)
        return validarInicioSesion(logged_user,nombreUsuario)
    else:
        return render_template('auth/login.html')
    

def validarInicioSesion(logged_user,nombreUsuario):
    if logged_user != None:
        if logged_user.contrasenia:

            login_user(logged_user)

            if not validarTiempoContraseña():
                flash("Su contraseña es muy antigua. Por favor, cámbiela.")
                return render_template('auth/login.html', abrir_modal=True)
            if UserDAO.existeUsuarioBloqueado(current_user.id_usuario,db):
                flash("Tu cuenta ha sido bloqueada. Por favor, contacta al departamento de TI para obtener asistencia.")
                return render_template('auth/login.html')

            permissions = UserDAO.get_with_permissions(current_user.id_usuario,db)
            current_user.permisos = permissions

            #Inserta Log Inicio de sesión exitoso -----------------------------------------
            insertarLogsAccesos(current_user.id_usuario,"Inicio de sesión exitoso",1,db)
            return redirect(url_for('home'))
        else:
            flash("Invalid password...")
    else:
        idUsuario = UserDAO.obtenerId_byNombre(nombreUsuario,db)
        if idUsuario:
            descripcion = "Inicio de sesión incorrecto"
            estatus = 0
            UserDAO.insertar_log(idUsuario,descripcion,estatus,db)
            numIntentosFallidos = UserDAO.contar_logs(idUsuario,descripcion,estatus,db)
            usuarioBloqueado = UserDAO.existeUsuarioBloqueado(idUsuario,db)
            if numIntentosFallidos >= 3 and not usuarioBloqueado:
                UserDAO.insertarUsuarioBloqueado(idUsuario,db)
            if usuarioBloqueado:
                flash("Tu cuenta ha sido bloqueada. Por favor, contacta al departamento de TI para obtener asistencia.")
                return render_template('auth/login.html')
            
            flash("Invalid password...")
            return render_template('auth/login.html')
            
        flash("User not found...")
        return render_template('auth/login.html')

def insertarLogsAccesos(idUsuario,descripcion,estatus,db):
    UserDAO.insertar_log(idUsuario,descripcion,estatus,db)

def validarTiempoContraseña():
    fechaPassword =  UserDAO.get_fecha_password(current_user.id_usuario,db)
    fechaActual = datetime.now()
    diferencia = fechaActual - fechaPassword
    if  diferencia > timedelta(days=90):
        return False
    return True

@app.route('/actualizarContrasenia', methods=['POST'])
def actualizar_contrasenia():
    if request.method == 'POST':
        nuevaContrasenia = request.form.get('nueva_contrasenia') 
        # Expresiones regulares para verificar los criterios de la contraseña
        tiene_mayuscula = re.search(r"[A-Z]", nuevaContrasenia)
        tiene_minuscula = re.search(r"[a-z]", nuevaContrasenia)
        tiene_numero = re.search(r"\d", nuevaContrasenia)
        es_longitud_valida = len(nuevaContrasenia) >= 4

        mensajes_error = []

        # Validar ataques XSS
        if re.search(r'[^a-zA-Z0-9\s]', nuevaContrasenia):
            mensajes_error.append("La contraseña no puede contener caracteres especiales.")
            return jsonify({'errors': mensajes_error})

        # Validar contra palabras relacionadas con consultas SQL
        palabras_sql = ['select', 'insert', 'update', 'drop', 'join', 'union', 'delete', 'truncate', 'exec', 'execute']
        for palabra in palabras_sql:
            if re.search(r'\b{}\b'.format(re.escape(palabra)), nuevaContrasenia.lower()):
                # Si se encuentra una palabra relacionada con SQL, agregar mensaje de error
                mensajes_error.append("La contraseña no puede contener palabras relacionadas con consultas SQL.")
                return jsonify({'errors': mensajes_error})
            
        contrasenias_comunes = cargarContraseñasComunes()
        if nuevaContrasenia in contrasenias_comunes:
            mensajes_error.append("La contraseña ingresada es común.")
            return jsonify({'errors': mensajes_error})
        
        contraseniaBD = UserDAO.get_password_by_username(current_user.nombre_usuario)
        if check_password_hash(contraseniaBD, nuevaContrasenia) and contraseniaBD :
            mensajes_error.append("La nueva contraseña no puede ser igual a la contraseña anterior.")
            return jsonify({'errors': mensajes_error})

        print("Nueva contraseña para el usuario: {}".format(nuevaContrasenia))
        if tiene_mayuscula and tiene_minuscula and tiene_numero and es_longitud_valida:

            UserDAO.actualizar_contrasenia(current_user.id_usuario,generate_password_hash(nuevaContrasenia),db)
            print("La nueva contraseña cumple con los criterios.")
            return jsonify({'exito': 'ok'})
        else:
            if not tiene_mayuscula:
                mensajes_error.append("La contraseña debe contener al menos una letra mayúscula.")
            if not tiene_minuscula:
                mensajes_error.append("La contraseña debe contener al menos una letra minúscula.")
            if not tiene_numero:
                mensajes_error.append("La contraseña debe contener al menos un número.")
            if not es_longitud_valida:
                mensajes_error.append("La contraseña debe tener más de 4 caracteres.")
            return jsonify({'errors': mensajes_error})


    return redirect(url_for('login'))


@app.route('/home')
def home():
    print("tipo Usuario {} ".format(current_user.rol))
    return redirect('/admin')
    

#Verificar permiso acceso módulos ------------------------------
def verificarPermisoUsuario(usuario_id, permiso, db):
    if current_user.is_authenticated:
        permissions = UserDAO.get_with_permissions(current_user.id_usuario, db)
        current_user.permisos = permissions

        ultimaSesion = UserDAO.obtenerUltimoInicioSesionExitosoAnterior(current_user.id_usuario,db)
        current_user.ultimaSesion = ultimaSesion

        if permiso in permissions: 
            return True
    return False
#Cerrar Sesión --------------------------------------------------
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
#Errores de búsqueda --------------------------------------------
def status_401(error):
    return render_template('errores/401.html'),401
def status_403(error):
    return render_template('errores/403.html'),403
def status_404(error):
    return render_template('errores/404.html'),404
#----------------------------------------------------------------

if __name__ == '__main__':
    csrf.init_app(app)
    db.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(403, status_403)
    app.register_error_handler(404, status_404)
    with app.app_context():
        db.create_all()
    app.run()
