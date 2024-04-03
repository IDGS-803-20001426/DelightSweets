from flask import Flask,Blueprint, render_template, request, redirect, url_for, flash,jsonify,abort
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required,current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.base import BaseView, expose
from flask_admin.form import Select2Widget
from flask_admin.form.upload import ImageUploadField
from flask_admin.form.upload import FileUploadField
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash,check_password_hash
from wtforms import PasswordField, StringField,SelectField,RadioField, SelectField, IntegerField, FloatField, DateField, DateTimeField, DateTimeLocalField, SelectMultipleField, FieldList, FormField, SubmitField, HiddenField
from wtforms.validators import DataRequired,Regexp,NumberRange
from functools import wraps
from markupsafe import Markup
from permissions import permission_required
from validaciones import validarPalabrasConsulta,validarFormulario,validarContrasenia,cargarContraseñasComunes,validarCamposLogin
from datetime import datetime, timedelta
import re
import forms
import base64
import json
from sqlalchemy import func, asc
import MySQLdb






# Models:
from models.Models import db,User,PermisoRol, Permiso, Rol,Proveedor,SolicitudProduccion, Receta, InventarioProductoTerminado, Galleta, MateriaPrima, RecetaMateriaIntermedia,MermaProdTerminado, Equivalencia, MermaProduccion, Inventario, Compra 
from models.entities.User import Usuario
from models.usersDao import UserDAO
from models.recetaDao import RecetaDAO
from models.produccionDao import ProduccionDAO
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
    base_template = 'admin/base.html'
    # @permission_required(1)

    def is_accessible(self):
        if current_user.is_authenticated:
            return True
        return False
        
admin = Admin(
    app,
    name='BakedSmiles',  # Nombre personalizado para el panel de administración
    base_template='admin/base.html',  # Plantilla base personalizada
    template_mode='bootstrap4'  # Modo de plantilla 
)

#Clase Usuarios ------------------------------------------------------------------------

class UserView(ModelView):
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
class ProveedorView(ModelView):
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
class PermisoView(ModelView):
    def is_accessible(self):
        permiso = 2
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    def scaffold_form(self):
        form_class = super(PermisoView, self).scaffold_form()        
        # Validaciones Personalizadas Ataques
        validarFormulario(form_class, ['permiso'])
        return form_class

#Clase Rol ------------------------------------------------------------------------
class RolView(ModelView):
    def is_accessible(self):
        permiso = 2
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    
    def scaffold_form(self):
        form_class = super(RolView, self).scaffold_form()        
        # Validaciones Personalizadas Ataques
        validarFormulario(form_class, ['nombre'])
        return form_class
#Clase MateriaPrima ------------------------------------------------------------------------
class MateriaPrimaView(ModelView):
    def is_accessible(self):
        permiso = 5
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    can_edit = False
    can_delete = False
    can_create = False    


class SolicitudProduccionForm(FlaskForm):
    id_receta = SelectField('Receta', choices=[], validators=[DataRequired()], coerce=int)
    fecha_solicitud = DateTimeLocalField('Fecha de Solicitud', format='%Y-%m-%dT%H:%M')

    def validate(self):
        if not super().validate():
            return False

        id_receta = self.id_receta.data
        receta = Receta.query.get(id_receta)
        if receta:
            galleta = receta.galleta
            if galleta:
                inventario = sum([inventario.cantidad for inventario in galleta.inventarios])
                if inventario >= 50:
                    flash('La galleta asociada a esta receta tiene más de 50 en inventario, por lo cual no es posible continuar con tu solicitud.', 'warning')
                    return False
        return True

class SolicitudProduccionView(ModelView):
    form = SolicitudProduccionForm
   
    column_formatters = {
        'id_receta': lambda v, c, m, p: m.receta.nombre_receta if m.receta else "Receta Desconocida",
    }
    column_labels = {
        'id_receta': 'Receta',
        'fecha_solicitud': 'Fecha de Solicitud',
    }
    column_list = ('id_receta', 'fecha_solicitud', 'fecha_terminacion', 'estatus')

    def is_accessible(self):
        permiso = 9
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)

    def on_form_prefill(self, form, id):
        form.id_receta.choices = [(receta.id_receta, receta.nombre_receta) for receta in Receta.query.all()]

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.id_receta.choices = [(receta.id_receta, receta.nombre_receta) for receta in Receta.query.all()]
        return form
    
    def edit_form(self, obj):
        form = super().edit_form(obj)
        form.id_receta.choices = [(receta.id_receta, receta.nombre_receta) for receta in Receta.query.all()]
        return form

    def on_model_change(self, form, model, is_created):
        id_receta = form.id_receta.data
        model.id_receta = id_receta
        model.fecha_solicitud = form.fecha_solicitud.data
        model.id_usuario = current_user.id_usuario
        model.estatus = 'Solicitada'

    can_edit = False


class InventarioProductoTerminadoView(ModelView):
    
    def _format_image(view, context, model, name):
        if model.imagen:
            return Markup(f'<img width="80" height="80" src="{model.imagen}"></img>')
        else:
            return "Receta Desconocida"

    @staticmethod
    def _format_cantidad(view, context, model, name):
        return f"{model.cantidad} pzs" if model.cantidad is not None else ""

    column_formatters = {
        'nombre': lambda v, c, m, p: m.nombre if m.nombre else "Receta Desconocida",
        'cantidad': _format_cantidad,
        'imagen': _format_image
    }

    column_labels = {
        'nombre': 'Galleta',
        'fecha_produccion': 'Fecha de Producción',
        'cantidad': 'Cantidad',
        'imagen': 'Imagen'
    }

    column_list = ['imagen', 'nombre', 'cantidad']

    def get_query(self):
        return (
            db.session.query(
                InventarioProductoTerminado.id_galleta,
                Galleta.imagen,
                Galleta.nombre,
                func.sum(InventarioProductoTerminado.cantidad).label('cantidad')
            )
            .join(Galleta, Galleta.id_galleta == InventarioProductoTerminado.id_galleta)
            .filter(InventarioProductoTerminado.estatus == 1)
            .group_by(
                InventarioProductoTerminado.id_galleta,
                Galleta.nombre,
                Galleta.imagen
            )
        )

    def is_accessible(self):
        return current_user.is_authenticated

    # Desactivar operaciones de CRUD
    can_create = False
    can_edit = False
    can_delete = False

class GalletaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    porcentaje_ganancia = FloatField('Porcentaje de Ganancia', validators=[DataRequired()])
    imagen = FileUploadField('Imagen', base_path="./src/static/img/galletas")

class GalletaView(ModelView):
    form=GalletaForm
    
    column_list = ('imagen', 'nombre', 'porcentaje_ganancia', 'costo_total_materias_primas', 'precio_final', 'utilidad')

    column_labels = {
        'costo_total_materias_primas': 'Costo Producción',
    }

    def is_accessible(self):
        permiso = 10
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)

    def on_model_change(self, form, model, is_created):
        model.nombre = sanitizarDatos(form.nombre.data)
        if form.imagen.data:
            with open("./src/static/img/galletas/" + model.imagen, 'rb') as f:
                imagen_data = f.read()
                imagen_base64 = base64.b64encode(imagen_data).decode('utf-8')
                content_type = form.imagen.data.content_type
                model.imagen = f'data:{content_type};base64,{imagen_base64}' 
    
    # Esta función le dice a Flask-Admin cómo mostrar la imagen en la tabla
    def _list_thumbnail(view, context, model, name):
        if not model.imagen:
            return ''
        # Renderizar la imagen en miniatura
        return Markup(f'<img width="80" height="80" src="{model.imagen}"></img>')

    def get_costo_materias_primas(self, context, model, name):
        costo_total = 0
        for receta in model.recetas:
            for materia_prima in receta.materias:
                costo_total += materia_prima.costo
        
        if model.recetas:  # Verifica si hay recetas asociadas
            c = costo_total / model.recetas[0].equivalencias.piezas
        else:
            c = 0  # Si no hay recetas, establece el costo por galleta como 0
        
        return c
    
    def get_precio_final(self, context, model, name):
        costo_total_materias_primas = self.get_costo_materias_primas(context, model, name)
        porcentaje_ganancia = model.porcentaje_ganancia
        # Calcula el precio final sumando el costo total de las materias primas y el porcentaje de ganancia
        precio_final = costo_total_materias_primas * (1 + porcentaje_ganancia / 100)

        if (precio_final - int(precio_final)) < 0.5 and precio_final > 0:
            precio_final = int(precio_final) + 0.5
        elif (precio_final - int(precio_final)) > 0.5 and precio_final > 0:
            precio_final = round(precio_final)

        return precio_final
    
    def get_utilidad(self, context, model, name):
        precio_final = self.get_precio_final(context, model, name)
        costo_total_materias_primas = self.get_costo_materias_primas(context, model, name)
        # Calcula la utilidad restando el costo total de las materias primas del precio final
        utilidad = precio_final - costo_total_materias_primas
        return round(utilidad, 1)

    column_formatters = {
        'imagen': _list_thumbnail,
        'costo_total_materias_primas': get_costo_materias_primas,
        'precio_final': get_precio_final,
        'utilidad': get_utilidad 
    }


@app.route('/materias_primas')
def obtener_materias_primas():
    materias_prim = MateriaPrima.query.all()
    opciones = [{'id': materia.id_materia, 'nombre': materia.nombre} for materia in materias_prim]
    return jsonify(opciones)

class RecetaForm(FlaskForm):
    nombre_receta = StringField('Nombre de la receta', validators=[DataRequired()])
    id_galleta = SelectField('Galleta', validators=[DataRequired()], choices=[])
    #materias_primas = QuerySelectField('Materias Primas', query_factory=lambda: MateriaPrima.query, widget=Select2Widget(multiple=True), render_kw={"form": "daniel"})
    #cantidad = FloatField("Cantidad", validators=[])
    #btn_materia = SubmitField('Registrar Materia', render_kw={"class": "btn btn-primary", "type": "button"})
    gramaje = FloatField('Gramaje', validators=[DataRequired()])
    piezas = IntegerField('Piezas', validators=[DataRequired()])
    datos_materias_primas = HiddenField('Id Materias')
     # Añadir un campo oculto para almacenar el ID de la materia prima seleccionada
    #materia_id = HiddenField('Materia ID')

    # Añadir un botón para abrir el modal
    btn_modal = SubmitField('Ingresar Materias', render_kw={"class": "btn btn-primary", "type": "button", "onclick": "abrirModal()"})

    def __init__(self, *args, **kwargs):
        super(RecetaForm, self).__init__(*args, **kwargs)
        #self.materias.choices = [(m.id_materia, m.nombre) for m in MateriaPrima.query.all()]
        self.id_galleta.choices = [(galleta.id_galleta, galleta.nombre) for galleta in Galleta.query.all()]

class RecetaView(ModelView):
    form = RecetaForm
    form_columns = ('btn_materia')
    def is_accessible(self):
        permiso = 6
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    def render(self, template, **kwargs):
        rendered = super().render(template, **kwargs)
        return rendered.replace('<form ', '<form id="daniel"')
    

    def _materias_primas_formatter(self, context, model, name):
        # Crear una lista de cadenas formateadas que contienen el nombre de la materia prima y la cantidad
        materias_primas = []
        for materia_prima in model.materias:
            cantidad = materia_prima.get_cantidad_en_receta(model.id_receta)
            materias_primas.append(f"{materia_prima.nombre} ({cantidad})")
        # Unir todas las cadenas en una sola cadena separada por comas
        return ', '.join(materias_primas)

    column_formatters = {
        'materias_primas': _materias_primas_formatter,
        'galleta': lambda v, c, m, p: m.galleta.nombre if m.galleta else "Receta Desconocida",
        'gramaje': lambda v, c, m, p: m.equivalencias.gramaje if m.equivalencias else "Gramaje desconocido",
        'piezas': lambda v, c, m, p: m.equivalencias.piezas if m.equivalencias else "Piezas desconocido",
    }

    column_list = ('nombre_receta', 'galleta', 'materias_primas', 'gramaje', 'piezas')

    def is_accessible(self):
        return current_user.is_authenticated
    
    def on_form_prefill(self, form, id):
        super().on_form_prefill(form, id)

        # Obtener el objeto del registro a editar
        obj = self.get_one(id)
        
        # Obtener los registros asociados a la receta específica
        registros_intermedios = (
            db.session.query(RecetaMateriaIntermedia.id_receta_producto_terminado,
                            RecetaMateriaIntermedia.id_receta,
                            RecetaMateriaIntermedia.id_materia,
                            MateriaPrima.nombre,
                            MateriaPrima.costo,
                            RecetaMateriaIntermedia.cantidad)
            .join(MateriaPrima, RecetaMateriaIntermedia.id_materia == MateriaPrima.id_materia)
            .filter(RecetaMateriaIntermedia.id_receta == obj.id_receta)
            .all()
        )

        # Crear una lista para almacenar los datos de materias primas
        datos = ""

        # Iterar sobre los registros intermedios y crear un diccionario con los datos de cada uno
        for registro in registros_intermedios:
            datos += '{"id_materia": "' + str(registro.id_materia) + '", "materia": "'+ str(registro.nombre) +'",  "cantidad": "' + str(registro.cantidad) + '"},'

        # Eliminar la última coma si hay al menos un registro
        if registros_intermedios:
            datos = datos[:-1]

        datos = "[" + datos + "]"

        # Asignar la lista de datos de materias primas al campo correspondiente del formulario
        form.datos_materias_primas.data = datos

        # Obtener la equivalencia asociada a la receta
        equivalencia = obj.equivalencias

        if equivalencia:
            # Asignar el valor de gramaje al campo correspondiente del formulario
            form.gramaje.data = equivalencia.gramaje
            form.piezas.data = equivalencia.piezas

    def on_model_change(self, form, model, is_created):
        model.nombre_receta = form.nombre_receta.data
        model.id_galleta = form.id_galleta.data

        # Asegurarse de que exista una instancia de Equivalencia asociada
        if not model.equivalencias:
           model.equivalencias = Equivalencia()
        
        model.equivalencias.piezas = form.piezas.data
        model.equivalencias.gramaje = form.gramaje.data 

    def after_model_change(self, form, model, is_created):
        RecetaMateriaIntermedia.query.filter_by(id_receta=model.id_receta).delete()
        json_materias = json.loads(form.datos_materias_primas.data)  
        print(form.datos_materias_primas.data)
        for objeto in json_materias:
            print(objeto)
        # Acceder a los valores de cada objeto
            id_materia = objeto['id_materia']
            cantidad_materia = objeto['cantidad']

            # Crear una nueva instancia de RecetaMateriaIntermedia
            receta_materia = RecetaMateriaIntermedia(
                id_receta=model.id_receta,
                id_materia=id_materia,
                cantidad=cantidad_materia
            )
            
            # Agregar el objeto a la sesión de la base de datos
            db.session.add(receta_materia)
            
        # Confirmar los cambios para guardar los objetos en la base de datos
        db.session.commit()

class MermaProdTerminadoForm(FlaskForm):
    tipo_merma = RadioField('Tipo de merma', choices=[('1', 'Lote'), ('2', 'Individual')], validators=[DataRequired()], default='1', render_kw={"style": "display: inline-block; border: none; list-style: none;"})
    select_galleta_individual = SelectField('Galleta', choices=[], validators=[DataRequired()], coerce=int)
    select_galleta_lote = SelectField('Galleta', choices=[], validators=[DataRequired()], coerce=int)
    cantidad_merma = IntegerField('Cantidad', validators=[NumberRange(min=1)], default=1)
    fecha = DateTimeLocalField('Fecha', format='%Y-%m-%dT%H:%M')
    motivo = StringField("Motivo", validators=[DataRequired()])

    def _query_inventario(self):
        return (
            db.session.query(
                InventarioProductoTerminado.id_galleta,
                Galleta.nombre,
                func.sum(InventarioProductoTerminado.cantidad).label('total_cantidad')
            )
            .join(Galleta, Galleta.id_galleta == InventarioProductoTerminado.id_galleta)
            .filter(InventarioProductoTerminado.estatus == 1)
            .group_by(
                InventarioProductoTerminado.id_galleta,
                Galleta.nombre
            )
        )
    
    def _query_inventario_lote(self):
        return (
            db.session.query(InventarioProductoTerminado.id_inventario_prod_terminado,
                           InventarioProductoTerminado.id_galleta,
                           InventarioProductoTerminado.fecha_produccion,
                           InventarioProductoTerminado.cantidad,
                           Galleta.nombre)\
                   .join(Galleta, InventarioProductoTerminado.id_galleta == Galleta.id_galleta)\
                   .filter(InventarioProductoTerminado.estatus == 1)\
                   .all()
        )

    def __init__(self, *args, **kwargs):
        super(MermaProdTerminadoForm, self).__init__(*args, **kwargs)
        # Ejecutar la consulta y asignar opciones al campo de selección
        
        choices = [(str(row.id_galleta), f"{row.nombre} - {row.total_cantidad} pzs en inventario") for row in self._query_inventario()]
        choices_lote = [(str(row.id_inventario_prod_terminado), f"{row.nombre} - {row.fecha_produccion} fecha producción - {row.cantidad} pzs en inventario") for row in self._query_inventario_lote()]
        self.select_galleta_individual.choices = choices
        self.select_galleta_lote.choices = choices_lote

    def validate(self):
        if not super().validate():
            return False

        id_galleta = self.select_galleta_individual.data
        
        # Obtener la cantidad total correspondiente a la galleta seleccionada y con estatus 1
        inventario_resultado = (
            self._query_inventario()
            .filter(
                InventarioProductoTerminado.id_galleta == id_galleta
            )
            .first()
        )
        
        if not inventario_resultado:
            flash('No hay inventario disponible para la galleta seleccionada.', 'error')
            return False

        total_cantidad = inventario_resultado.total_cantidad
        
        if self.cantidad_merma.data > total_cantidad:
            flash('La cantidad de merma es mayor que la cantidad en inventario.', 'error')
            return False
        
        return True

class MermaProdTerminadoView(ModelView):
    form = MermaProdTerminadoForm
    column_list = ('galleta', 'cantidad', 'fecha', 'motivo')

    column_formatters = {
        'galleta': lambda v, c, m, p: m.inventario_prod_terminado.galleta.nombre if m.inventario_prod_terminado else "Galleta Desconocida"
    }

    def _inv_galleta_ind(self, id_galleta_param):
        return (
                InventarioProductoTerminado.query
                .filter(
                    InventarioProductoTerminado.id_galleta == id_galleta_param,
                    InventarioProductoTerminado.estatus == 1
                )
                .order_by(InventarioProductoTerminado.fecha_produccion)
                .all()
            )
    
    def _inv_galleta_lote(self, id_inv_param):
        return (
                InventarioProductoTerminado.query
                .filter(
                    InventarioProductoTerminado.id_inventario_prod_terminado == id_inv_param,
                    InventarioProductoTerminado.estatus == 1
                )
                .first()
            )
    
    def on_model_change(self, form, model, is_created):  

        if form.tipo_merma.data == "1":
            model.id_inventario_prod_terminado = form.select_galleta_individual.data
            model.cantidad = 0
            inventarios = self._inv_galleta_lote(form.select_galleta_lote.data)

            model.cantidad = inventarios.cantidad 
            inventarios.estatus = 0
            inventarios.cantidad = 0

        elif form.tipo_merma.data == "2":

            model.id_inventario_prod_terminado = 1
            model.cantidad = form.cantidad_merma.data
            inventarios = self._inv_galleta_ind(form.select_galleta_individual.data)

            cantidad_restante = model.cantidad
                    
            for inventario in inventarios:
                if cantidad_restante > 0:
                    #inventario_anterior = inventario  # Guardamos la referencia al inventario actual
                    cantidad_a_restar = min(cantidad_restante, inventario.cantidad)
                    inventario.cantidad -= cantidad_a_restar
                    cantidad_restante -= cantidad_a_restar

                if inventario.cantidad == 0:
                    #inventario_agotado = inventario_anterior  # Usamos la referencia al inventario anterior
                    print("id in: {}".format(inventario.id_inventario_prod_terminado))
                    db.session.query(InventarioProductoTerminado).filter(InventarioProductoTerminado.id_inventario_prod_terminado == inventario.id_inventario_prod_terminado).update({InventarioProductoTerminado.estatus: 0})
                    break

            if is_created:
                model.id_inventario_prod_terminado = inventarios[0].id_inventario_prod_terminado

class MermaProduccionForm(FlaskForm):
    tipo_merma_materia = RadioField('Tipo de merma', choices=[('1', 'Lote'), ('2', 'Individual')], validators=[DataRequired()], default='1', render_kw={"style": "display: inline-block; border: none; list-style: none;"})
    select_materia_individual = SelectField('Materia Prima', choices=[], validators=[DataRequired()], coerce=int)
    select_materia_lote = SelectField('Materia Prima', choices=[], validators=[DataRequired()], coerce=int)
    cantidad_merma_materia = IntegerField('Cantidad', validators=[NumberRange(min=1), DataRequired()], default=1)
    fecha = DateTimeLocalField('Fecha', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    motivo = StringField("Motivo", validators=[DataRequired()])

    def _query_lote_materias(self):
        return db.session.query(
                    Inventario.id_inventario,
                    MateriaPrima.nombre,
                    Inventario.fecha_caducidad,
                    Inventario.cantidad
                ).join(MateriaPrima, Inventario.id_materia == MateriaPrima.id_materia)\
                .join(Proveedor, Inventario.id_proveedor == Proveedor.id_proveedor)\
                .filter(Inventario.estatus == 1).all()

    def _query_materias(self, id_materia):
        query = db.session.query(
                Inventario.id_materia,
                MateriaPrima.nombre.label('nombre_materia'),
                func.sum(Inventario.cantidad).label('total_cantidad'),
                func.count(Inventario.id_inventario).label('total_inventarios'),
                func.max(Proveedor.nombre).label('nombre_proveedor'),
                func.max(Inventario.fecha_caducidad).label('fecha_caducidad')
            ).join(MateriaPrima, Inventario.id_materia == MateriaPrima.id_materia)\
            .join(Proveedor, Inventario.id_proveedor == Proveedor.id_proveedor)\
            .filter(Inventario.estatus == 1)\
            .group_by(Inventario.id_materia, MateriaPrima.nombre)\
            .order_by(func.max(Inventario.fecha_caducidad).desc())
            
        if id_materia is not None:
            query = query.filter(Inventario.id_materia == id_materia)
            return query.first()
        else:
            return query.all()

    def __init__(self, *args, **kwargs):
        super(MermaProduccionForm, self).__init__(*args, **kwargs)
        choices_individual = [(str(row.id_materia), f"{row.nombre_materia}") for row in self._query_materias(None)]
        choices_lote = [(str(row.id_inventario), f"{row.nombre} - Caducidad: {row.fecha_caducidad} - {row.cantidad} en inventario") for row in self._query_lote_materias()]
        self.select_materia_individual.choices = choices_individual
        self.select_materia_lote.choices = choices_lote

    def validate(self):
        if not super().validate():
            return False

        if self.tipo_merma_materia.data == "2":
            id_materia = self.select_materia_individual.data
            
            # Obtener la cantidad total correspondiente a la galleta seleccionada y con estatus 1
            inventario_res = self._query_materias(id_materia)
            if not inventario_res:
                flash('No hay inventario disponible para la materia seleccionada.', 'error')
                return False

            total_cantidad = inventario_res.total_cantidad
            
            if self.cantidad_merma_materia.data > total_cantidad:
                flash('La cantidad de merma es mayor que la cantidad en inventario.', 'error')
                return False
            
            return True
        return True
    
class MermaProduccionView(ModelView):
    form = MermaProduccionForm

    column_list = ('id_materia', 'cantidad', 'fecha', 'motivo')

    column_formatters = {
        'id_materia': lambda v, c, m, p: m.materia_prima.nombre if m.materia_prima else "Galleta Desconocida"
    }


    def on_model_change(self, form, model, is_created):
        if form.tipo_merma_materia.data == "1":
            model.id_materia = form.select_materia_individual.data
            model.cantidad = 0
            inventario_seleccionado = db.session.query(
                Inventario
            ).filter(
                Inventario.id_inventario == form.select_materia_lote.data
            ).first()

            if inventario_seleccionado:
                # Asignar los valores del inventario seleccionado al modelo
                model.id_materia = inventario_seleccionado.id_materia
                model.cantidad = inventario_seleccionado.cantidad
                model.fecha = form.fecha.data
                model.motivo = form.motivo.data

                # Actualizar el estatus y la cantidad del inventario seleccionado a 0
                inventario_seleccionado.estatus = 0
                inventario_seleccionado.cantidad = 0

                # Guardar los cambios en la base de datos
                db.session.commit()
        elif form.tipo_merma_materia.data == "2":
            model.id_materia = form.select_materia_individual.data
            model.cantidad = form.cantidad_merma_materia.data
            model.fecha = form.fecha.data
            model.motivo = form.motivo.data

            cantidad_merma = form.cantidad_merma_materia.data
            id_materia = form.select_materia_individual.data

            # Obtener los registros de inventario correspondientes a la materia prima seleccionada
            inventario_registros = db.session.query(Inventario).filter(
                Inventario.id_materia == id_materia,
                Inventario.estatus == 1
            ).order_by(asc(Inventario.fecha_caducidad)).all()

            for inventario in inventario_registros:
                if cantidad_merma <= 0:
                    break
                
                cantidad_restante = cantidad_merma - inventario.cantidad
                if cantidad_restante >= 0:
                    # Restar la cantidad de merma del inventario actual
                    cantidad_merma = cantidad_restante
                    inventario.cantidad = 0
                    inventario.estatus = 0 if inventario.cantidad == 0 else 1
                else:
                    # Si la cantidad de merma es menor que la del inventario actual,
                    # simplemente restar la cantidad de merma y salir del bucle
                    inventario.cantidad -= cantidad_merma
                    break




def sanitizarDatos(inputString):
    caracteresNoAceptados = ["select", "insert", "update", "delete", "drop", 
                             "SELECT","INSERT","UPDATE","DELETE","DROP",
                             "Select","Insert","Update","Delete","Drop",
                             "<", ">", ";", "'", '"', "*" ]

    # Reemplaza cada palabra prohibida con una cadena vacía
    cadenaSanitizadda = inputString
    for palabra in caracteresNoAceptados:
        cadenaSanitizadda = cadenaSanitizadda.replace(palabra, '')

    return cadenaSanitizadda


# Define una clase Form personalizada para el formulario de compras
class CompraForm(FlaskForm):
    nombre_producto = SelectField('Nombre del Producto', coerce=int, validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired()])
    precio_compra = FloatField('Precio de Compra', validators=[DataRequired()])
    fecha_compra = DateField('Fecha de Compra', validators=[DataRequired()])
    fecha_caducidad = DateField('Fecha de Caducidad', validators=[DataRequired()])
    proveedor = SelectField('Proveedor', coerce=int, validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super(CompraForm, self).__init__(*args, **kwargs)
        # Consultar los nombres de productos disponibles en la base de datos
        productos = MateriaPrima.query.all()
        # Crear una lista de opciones para el campo de selección de productos
        opciones_productos = [(producto.id_materia, producto.nombre) for producto in productos]
        # Establecer las opciones en el campo de selección de productos
        self.nombre_producto.choices = opciones_productos

        # Consultar los proveedores disponibles en la base de datos
        proveedores = Proveedor.query.all()
        # Crear una lista de opciones para el campo de selección de proveedores
        opciones_proveedores = [(proveedor.id_proveedor, proveedor.nombre) for proveedor in proveedores]
        # Establecer las opciones en el campo de selección de proveedores
        self.proveedor.choices = opciones_proveedores

        # Establecer la fecha actual como valor predeterminado para la fecha de compra
        self.fecha_compra.data = datetime.today().date()

    def validate(self):
        if not super().validate():
            return False
        
        if self.fecha_compra.data < datetime.today().date():
            flash('La fecha de compra no puede ser anterior a la fecha actual.', 'error')
            return False

        return True

# Define una clase ModelView personalizada para las compras
class CompraView(ModelView):
    form = CompraForm
    column_list = ('nombre_producto', 'cantidad', 'precio_compra', 'fecha_compra', 'fecha_caducidad', 'nombre_proveedor')

    def on_model_change(self, form, model, is_created):
        # Obtener el nombre del producto seleccionado en el formulario
        id_materia = form.nombre_producto.data
        nombre_producto = MateriaPrima.query.filter_by(id_materia=id_materia).first().nombre
        
        # Asignar el nombre del producto a la instancia del modelo Compra
        model.nombre_producto = nombre_producto



#### Añadir views to admin --------------------------------------------------------------------------------------
# admin.add_view(UserView(User,db.session,menu_icon_type='fa', menu_icon_value='fa-user',name="Usuarios"))
# admin.add_view(RolView(Rol,db.session,category='Adm. Permisos ',name="Rol"))
# admin.add_view(PermisoView(Permiso,db.session,category='Adm. Permisos ',name="Permiso"))
# admin.add_view(PermisoRolView(PermisoRol,db.session,category='Adm. Permisos ',name="Permisos-Roles"))
# admin.add_view(ProveedorView(Proveedor,db.session,menu_icon_type='fa', menu_icon_value='fa-id-card-o',name="Proveedor"))
# admin.add_view(MateriaPrimaView(MateriaPrima,db.session,menu_icon_type='fa', menu_icon_value='fa-shopping-basket ',name="Materia Prima"))

# admin.add_view(RecetaView(Receta, db.session,menu_icon_type='fa', menu_icon_value='fa-spoon',name="Recetas"))
# admin.add_view(SolicitudProduccionView(SolicitudProduccion, db.session, menu_icon_type='fa', menu_icon_value='fa-plus',name="Solicitud Producción"))
# admin.add_view(InventarioProductoTerminadoView(InventarioProductoTerminado, db.session,menu_icon_type='fa', menu_icon_value='fa-calculator',name="Inventario en venta"))
# admin.add_view(GalletaView(Galleta, db.session,menu_icon_type='fa', menu_icon_value='fa-cutlery',name="Galletas"))
# admin.add_view(MermaProdTerminadoView(MermaProdTerminado, db.session, menu_icon_type='fa', menu_icon_value='fa-plus-square-o',name="Merma Galletas"))
# admin.add_view(MermaProduccionView(MermaProduccion, db.session, name="Merma Materias"))

# Define tus blueprints
admin_blueprints = [
    UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-user', name="Usuarios"),
    RolView(Rol, db.session, category='Adm. Permisos ', name="Rol"),
    PermisoView(Permiso, db.session, category='Adm. Permisos ', name="Permiso"),
    PermisoRolView(PermisoRol, db.session, category='Adm. Permisos ', name="Permisos-Roles"),
    ProveedorView(Proveedor, db.session, menu_icon_type='fa', menu_icon_value='fa-id-card-o', name="Proveedor"),
    MateriaPrimaView(MateriaPrima, db.session, menu_icon_type='fa', menu_icon_value='fa-shopping-basket ', name="Materia Prima"),
    RecetaView(Receta, db.session, menu_icon_type='fa', menu_icon_value='fa-spoon', name="Recetas"),
    SolicitudProduccionView(SolicitudProduccion, db.session, menu_icon_type='fa', menu_icon_value='fa-plus', name="Solicitud Producción"),
    InventarioProductoTerminadoView(InventarioProductoTerminado, db.session, menu_icon_type='fa', menu_icon_value='fa-calculator', name="Inventario en venta"),
    GalletaView(Galleta, db.session, menu_icon_type='fa', menu_icon_value='fa-cutlery', name="Galletas"),
    MermaProdTerminadoView(MermaProdTerminado, db.session, menu_icon_type='fa', menu_icon_value='fa-plus-square-o', name="Merma Galletas"),
    MermaProduccionView(MermaProduccion, db.session, name="Merma Materias"),
    CompraView(Compra, db.session, menu_icon_type='fa', menu_icon_value='fa-shopping-cart', name="Compras")
]
# Agrega tus blueprints a Flask-Admin
for blueprint in admin_blueprints:
    admin.add_view(blueprint)


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
#Modulos personalizados------------------------------------------------------------------------------------

produccion_bp = Blueprint('produccion', __name__)
@produccion_bp.route('/produccion', methods=["GET", "POST"])
@login_required
@permission_required(7)
def produccion():
    form=forms.ProduccionModificarForm(request.form)
    modProduccion = ProduccionDAO.obtenerRecetasConSolicitudes(db)
    if request.method == 'POST':
        mensajes_error = []
        estatusTxt = {
            0: 'Solicitada',
            1: 'Terminada',
            2: 'Cancelada'
        }
        if form.estatusProduccion.data == "":
            mensajes_error.append("Selecciona un estatus.")
            return jsonify({'errors': mensajes_error})
        
        estatus = int(form.estatusProduccion.data)
        estatusTexto = estatusTxt.get(estatus,'Estatus Desconocido')
        idProd = int(form.id.data)
        estatusDB = ProduccionDAO.obtenerEstatusPorId(db,idProd)
        
        if estatusTexto == estatusDB:
            mensajes_error.append("La solicitud ya cuenta con este estatus.")
            return jsonify({'errors': mensajes_error})
        if estatusDB == 'Terminada' or estatusDB == 'Cancelada':
            mensajes_error.append("El estatus ya no puede ser cambiado.")
            return jsonify({'errors': mensajes_error})

        #Permite actualizar el estatus del registro
        ProduccionDAO.actualizarEstatusYFecha(db,idProd,estatusTexto)
        #Obtener datos producción & receta-------------------------------------------------
        datosSolicitud, datosReceta = ProduccionDAO.obtenerSolicitudPorID(db, idProd)
        numPiezas = ProduccionDAO.obtenerNumeroPiezasPorReceta(db,datosSolicitud.id_receta)
        #Insertar inventario_producto_terminado
        ProduccionDAO.insertarRegistroInventarioProductoTerminado(db,datosReceta.id_galleta,numPiezas,estatus)
        if estatus == 1:
            actualizarInventario(db, datosReceta.id_receta)
        
        return jsonify({'exito': 'ok'})
    return render_template('admin/moduloProduccion.html', form=form, modProduccion=modProduccion)

 


class ProduccionAdminView(BaseView):
    @login_required
    @permission_required(7)
    @expose('/')
    def index(self):
        form=forms.ProduccionModificarForm(request.form)
        modProduccion = ProduccionDAO.obtenerRecetasConSolicitudes(db)
        if request.method == 'POST':
            mensajes_error = []
            estatusTxt = {
                0: 'Solicitada',
                1: 'Terminada',
                2: 'Cancelada'
            }
            if form.estatusProduccion.data == "":
                mensajes_error.append("Selecciona un estatus.")
                return jsonify({'errors': mensajes_error})
            
            estatus = int(form.estatusProduccion.data)
            estatusTexto = estatusTxt.get(estatus,'Estatus Desconocido')
            idProd = int(form.id.data)
            estatusDB = ProduccionDAO.obtenerEstatusPorId(db,idProd)
            
            if estatusTexto == estatusDB:
                mensajes_error.append("La solicitud ya cuenta con este estatus.")
                return jsonify({'errors': mensajes_error})
            if estatusDB == 'Terminada' or estatusDB == 'Cancelada':
                mensajes_error.append("El estatus ya no puede ser cambiado.")
                return jsonify({'errors': mensajes_error})

            #Permite actualizar el estatus del registro
            ProduccionDAO.actualizarEstatusYFecha(db,idProd,estatusTexto)
            #Obtener datos producción & receta-------------------------------------------------
            datosSolicitud, datosReceta = ProduccionDAO.obtenerSolicitudPorID(db, idProd)
            numPiezas = ProduccionDAO.obtenerNumeroPiezasPorReceta(db,datosSolicitud.id_receta)
            #Insertar inventario_producto_terminado
            ProduccionDAO.insertarRegistroInventarioProductoTerminado(db,datosReceta.id_galleta,numPiezas,estatus)
            if estatus == 1:
                actualizarInventario(db, datosReceta.id_receta)
            
            return jsonify({'exito': 'ok'})
        return self.render('admin/moduloProduccion.html', form=form, modProduccion=modProduccion)

# Registrar la vista de Flask-Admin para tu blueprint produccion_bp
admin.add_view(ProduccionAdminView(name='Produccion', endpoint='produccion_admin'))

def actualizarInventario(db, id_receta):
    # Obtener las materias primas requeridas por la receta
    materias_primas_requeridas = ProduccionDAO.obtenerMateriasPrimasPorReceta(db, id_receta)
    
    # Iterar sobre cada materia prima requerida
    for materia_prima in materias_primas_requeridas:
        id_materia = materia_prima.id_materia
        cantidad_requerida = materia_prima.cantidad
        
        # Obtener el inventario de la materia prima ordenado por fecha de caducidad
        inventario = ProduccionDAO.obtenerMateriasPrimasInventario(db, id_materia)
        
        # Verificar si hay suficiente cantidad disponible en el inventario
        cantidad_disponible_total = sum(item.cantidad for item in inventario)
        if cantidad_disponible_total < cantidad_requerida:
            print(f"No hay suficiente cantidad disponible de la materia prima con ID {id_materia}.")
            continue
        
        # Consumir la cantidad necesaria de la materia prima
        cantidad_consumida = 0
        for item in inventario:
            if cantidad_requerida <= 0:
                break
            
            if item.cantidad <= cantidad_requerida:
                cantidad_consumida += item.cantidad
                cantidad_requerida -= item.cantidad
                item.cantidad = 0
            else:
                cantidad_consumida += cantidad_requerida
                item.cantidad -= cantidad_requerida
                cantidad_requerida = 0
        
        # Guardar los cambios en la base de datos para esta materia prima
        db.session.commit()




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
        print(current_user.permisos)
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
    app.register_blueprint(produccion_bp)
    app.register_error_handler(401, status_401)
    app.register_error_handler(403, status_403)
    app.register_error_handler(404, status_404)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
