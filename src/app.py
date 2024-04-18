from flask import Flask,Blueprint, render_template, request, redirect, url_for, flash,jsonify,abort,session,request, make_response, jsonify
from flask_wtf.csrf import CSRFProtect,generate_csrf
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
from sqlalchemy.exc import SQLAlchemyError
import re
import forms
import base64
import json
from sqlalchemy import func, asc,case,text
import MySQLdb
import json
from flask_admin.form import FormOpts
from flask_admin.helpers import (get_form_data, validate_form_on_submit,
                                 get_redirect_target, flash_errors)
from flask_admin.babel import gettext, ngettext
from helpers import prettify_name, get_mdict_item_or_list
from sqlalchemy import update,case,text



# Models:
from models.Models import db,User,PermisoRol, Permiso, Rol,Proveedor,SolicitudProduccion, Receta, InventarioProductoTerminado, Galleta, MateriaPrima, RecetaMateriaIntermedia,MermaProdTerminado, Equivalencia, MermaProduccion, Inventario, Compra, Venta , EquivalenciaMedida , DetalleVenta 
from models.entities.User import Usuario
from models.usersDao import UserDAO
from models.recetaDao import RecetaDAO
from models.produccionDao import ProduccionDAO
from models.galletaDao import GalletaDAO,DetalleVentaDAO,VentaDAO,InventarioProductoTerminadoDAO,CorteCajaDAO,CorteCajaVentaDAO,RetiroDAO,MateriaPrimaDAO,ProveedorDAO
from config import DevelopmentConfig

# PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from flask import send_file
from reportlab.lib.styles import getSampleStyleSheet
import os
from datetime import datetime
import base64

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
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'

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

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)
#Clase Permisos Rol ------------------------------------------------------------------------
class PermisoRolCreateForm(FlaskForm):
    id_rol = SelectField('Rol', choices=[], validators=[DataRequired()])
    id_permiso = SelectField('Permiso', choices=[], validators=[DataRequired()])

class PermisoRolView(ModelView):
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'

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
    
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)
    
#Clase Proveedores ------------------------------------------------------------------------
class ProveedorView(ModelView):
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'
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

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)

#Clase Permiso ------------------------------------------------------------------------
class PermisoView(ModelView):
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'

    def is_accessible(self):
        permiso = 2
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    def scaffold_form(self):
        form_class = super(PermisoView, self).scaffold_form()        
        # Validaciones Personalizadas Ataques
        validarFormulario(form_class, ['permiso'])
        return form_class
    
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)

#Clase Rol ------------------------------------------------------------------------
class RolView(ModelView):
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'
    def is_accessible(self):
        permiso = 2
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    
    def scaffold_form(self):
        form_class = super(RolView, self).scaffold_form()        
        # Validaciones Personalizadas Ataques
        validarFormulario(form_class, ['nombre'])
        return form_class
    
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)
    
    
    
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired, InputRequired, NumberRange, ValidationError
from datetime import datetime


class MateriaPrimaForm(FlaskForm):
    nombre = StringField('Nombre de la Materia Prima', validators=[DataRequired()])
    costo = FloatField('Costo', validators=[InputRequired(message="Debe ingresar un costo válido."), NumberRange(min=0.01, message="El costo debe ser mayor que cero.")])
    tipo_medida = SelectField('Tipo de Medida', coerce=int, validators=[DataRequired()])
    fecha_registro = DateField('Fecha de Registro', default=datetime.today().date(), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(MateriaPrimaForm, self).__init__(*args, **kwargs)
        self.setup_choices()

    def setup_choices(self):
        tipos_medida = EquivalenciaMedida.query.all()
        opciones_tipos_medida = [(tipo.id_equivalencia, tipo.unidad) for tipo in tipos_medida]
        opciones_tipos_medida.insert(0, (-1, 'Elige una opción'))
        self.tipo_medida.choices = opciones_tipos_medida

    def validate_fecha_registro(self, field):
        if field.data > datetime.today().date():
            raise ValidationError('La fecha de registro no puede ser en el futuro.')

class MateriaPrimaView(ModelView):
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'
    
    def is_accessible(self):
        permiso = 5
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    can_edit = False
    can_delete = False
    can_create = True    

    form = MateriaPrimaForm
   
    column_list = ('nombre', 'costo', 'tipo_medida')

    def on_model_change(self, form, model, is_created):
        model.nombre = form.nombre.data
        model.costo = form.costo.data
        model.tipo_medida = form.tipo_medida.data
       

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
        Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url))
                else:
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args, form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)

    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)


class SolicitudProduccionForm(FlaskForm):
    id_receta = SelectField('Receta', choices=[], validators=[DataRequired()], coerce=int)
    fecha_solicitud = DateTimeLocalField('Fecha de Solicitud', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])

    def validate(self):
        if not super().validate():
            return False

        if self.fecha_solicitud.data < datetime.now():
            flash('La fecha de solicitud no puede ser anterior a la fecha y hora actual.', 'warning')
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
                if not materiaPrimaSuficiente(db,id_receta):
                    flash('No hay la cantidad necesaria de ingredientes para elaborar esta receta.', 'warning')
                    return False
        return True

class SolicitudProduccionView(ModelView):
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'

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
        permiso = 8
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

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)
    
from flask_admin.base import BaseView
from flask_admin import expose
from datetime import datetime, timedelta
import calendar
import locale

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

class VentasView(BaseView):
    def is_accessible(self):
        permiso = 12
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)
    @expose('/')
    def index(self):
        # Consulta las ventas por día desde tu base de datos usando SQLAlchemy
        ventas_diarias = db.session.query(Venta.fecha_venta, db.func.sum(Venta.total)).group_by(Venta.fecha_venta).all()

        # Formatea los datos de ventas diarias en un formato que pueda entender Chart.js
        labels_diarias = [venta[0].strftime('%d/%m/%Y') for venta in ventas_diarias]  # Formato "01/05/2024"
        data_diarias = [venta[1] for venta in ventas_diarias]

        # Calcular la fecha de inicio de la semana actual y hace 6 semanas atrás
        today = datetime.now()
        start_of_current_week = today - timedelta(days=today.weekday())
        start_of_6_weeks_ago = start_of_current_week - timedelta(weeks=6)
        
        # Consulta las ventas por semana desde tu base de datos usando SQLAlchemy
        ventas_semanales = db.session.query(
            db.func.year(Venta.fecha_venta).label('year'), 
            db.func.week(Venta.fecha_venta).label('week'), 
            db.func.sum(Venta.total)
        ).filter(
            Venta.fecha_venta >= start_of_6_weeks_ago,
            Venta.fecha_venta <= start_of_current_week
        ).group_by('year', 'week').all()

        # Formatear los datos de ventas semanales en un formato que pueda entender Chart.js
        labels_semanales = []
        data_semanales = []
        for venta in ventas_semanales:
            # Generar la etiqueta de la semana (Año-Semana)
            week_label = f"{venta.year}-W{venta.week}"
            labels_semanales.append(week_label)
            data_semanales.append(venta[2])  # Total de ventas por semana

        #Galleta Más Vendida ----------------------------------------------------------------------------
        consultaSql1 = text("""
            SELECT d.id_galleta, 
            g.nombre AS Nombre_Galleta,
            SUM(CASE 
                    WHEN d.medida = 'gramos' THEN 
                        d.cantidad / (e.gramaje / e.piezas)
                    ELSE d.cantidad
                END
                ) AS Cantidad_Vendida
            FROM detalle_venta AS d
            INNER JOIN galleta AS g ON d.id_galleta = g.id_galleta
            INNER JOIN receta AS r ON g.id_galleta = r.id_galleta
            INNER JOIN equivalencia AS e ON r.id_receta = e.id_receta
            GROUP BY d.id_galleta, g.nombre
            ORDER BY Cantidad_Vendida DESC
            """)
        
        consulta_galleta_vendida = db.session.query(
            Galleta.id_galleta,
            Galleta.nombre.label('Nombre_Galleta'),
            func.sum(
                case(
                    (DetalleVenta.medida == 'gramos', DetalleVenta.cantidad / (Equivalencia.gramaje / Equivalencia.piezas)),
                    else_=DetalleVenta.cantidad
                )
            ).label('Cantidad_Vendida')
        ).from_statement(consultaSql1)

        # Ejecutar la consulta y obtener los resultados
        resultadoGalletaMasVendida = consulta_galleta_vendida.all()

        labels_galletaMasVendida = []
        data_galletaMasVendida = []
        for venta in resultadoGalletaMasVendida:
            labels_galletaMasVendida.append(venta.Nombre_Galleta)
            data_galletaMasVendida.append(str(venta.Cantidad_Vendida))

        #Costo Producción Galleta -----------------------------------------------------------------------
        consultaSql2 = text("""
            SELECT 
            g.nombre AS galleta,
            ROUND(SUM((rmi.cantidad * mp.costo)/e.piezas), 2) AS costo
                FROM galleta g
                JOIN receta r ON g.id_galleta = r.id_galleta
                JOIN receta_materia_intermedia rmi ON r.id_receta = rmi.id_receta
                JOIN materia_prima mp ON rmi.id_materia = mp.id_materia
                JOIN equivalencia AS e ON e.id_receta = r.id_receta
                GROUP BY g.nombre
                ORDER BY costo DESC;
        """)

        resultadoCostoProduccion = db.session.execute(consultaSql2)

        labels_galletaCostoProduccion = []
        data_galletaCostoProduccion = []
        for venta in resultadoCostoProduccion:
            labels_galletaCostoProduccion.append(venta.galleta)
            data_galletaCostoProduccion.append(str(venta.costo))


        #Galleta que genera mas Utilidad -----------------------------------------------------------------------
        consultaSql3 = text("""
            SELECT 
            g.id_galleta,
            g.nombre AS galleta,
            ROUND(SUM((rmi.cantidad * mp.costo)/e.piezas), 2) AS Costo_Produccion,
            ROUND(SUM(g.porcentaje_ganancia * ((rmi.cantidad * mp.costo)/e.piezas) ) , 2) AS Utilidad,
            ROUND(SUM(g.porcentaje_ganancia * ((rmi.cantidad * mp.costo)/e.piezas) ) + SUM((rmi.cantidad * mp.costo)/e.piezas), 2) AS Costo_Galleta
                FROM galleta g
                JOIN receta r ON g.id_galleta = r.id_galleta
                JOIN receta_materia_intermedia rmi ON r.id_receta = rmi.id_receta
                JOIN materia_prima mp ON rmi.id_materia = mp.id_materia
                JOIN equivalencia AS e ON e.id_receta = r.id_receta
                GROUP BY g.id_galleta,g.nombre
                ORDER BY Utilidad;
        """)

        # Ejecutar la consulta
        resultadoUtilidadGalleta = db.session.execute(consultaSql3)

        labels_galletaUtilidad = []
        data_galletaUtilidad = []
        for venta in resultadoUtilidadGalleta:
            labels_galletaUtilidad.append(venta.galleta)
            data_galletaUtilidad.append(str(venta.Utilidad))
            
                    
            # Empleado encargado de generar las galletas -----------------------------------------------------------------------
            consultaSql4 = text("""
                SELECT 
                    sp.id_solicitud AS Solicitud, 
                    u.nombre_completo AS Empleado_Reponsable, 
                    r.nombre_receta AS Receta, 
                    g.nombre AS Galleta
                FROM 
                    solicitud_prooduccion AS sp
                INNER JOIN 
                    usuario AS u ON sp.id_usuario = u.id_usuario
                INNER JOIN 
                    receta AS r ON sp.id_receta = r.id_receta
                INNER JOIN 
                    galleta AS g ON g.id_galleta = r.id_galleta
                WHERE 
                    sp.estatus = 'Terminada';
            """)

        
            resultado_empleado_galleta = db.session.execute(consultaSql4)

            
            datos_solicitudes = []

          
            for solicitud in resultado_empleado_galleta:
                datos_solicitud = {
                    'Solicitud': solicitud.Solicitud,
                    'Empleado_Resposable': solicitud.Empleado_Reponsable, 
                    'Receta': solicitud.Receta,
                    'Galleta': solicitud.Galleta
                }
                datos_solicitudes.append(datos_solicitud)

        
        #Galleta que genera mas Merma -----------------------------------------------------------------------
        consultaSql5 = text("""
            SELECT 
            g.id_galleta,
                g.nombre AS galleta,
                SUM(mpt.cantidad) AS total_merma,
                ROUND( (SUM(mpt.cantidad) / (SELECT SUM(cantidad) FROM merma_prod_terminado)) * 100, 2) AS porcentaje_merma,
                MAX(cpg.Costo_Produccion) AS Costo_Produccion,
                ROUND(SUM(mpt.cantidad) * MAX(cpg.Costo_Produccion), 2) AS Costo_Perdido
            FROM merma_prod_terminado AS mpt
            JOIN inventario_producto_terminado AS ipt ON mpt.id_inventario_prod_terminado = ipt.id_inventario_prod_terminado
            JOIN galleta AS g ON ipt.id_galleta = g.id_galleta
            JOIN 
                (
                    SELECT 
                    g.id_galleta,
                    g.nombre AS galleta,
                    ROUND(SUM(mp.costo * rmi.cantidad) / MAX(e.piezas), 2) AS Costo_Produccion,
                            ROUND(((SUM(mp.costo * rmi.cantidad) / MAX(e.piezas)) * MAX(g.porcentaje_ganancia) / 100), 2) AS Utilidad,
                                    ROUND((SUM(mp.costo * rmi.cantidad) / MAX(e.piezas)) + (((SUM(mp.costo * rmi.cantidad) / MAX(e.piezas)) * MAX(g.porcentaje_ganancia) / 100)), 2) AS Costo_Galleta
                        FROM galleta g
                        JOIN receta r ON g.id_galleta = r.id_galleta
                        JOIN receta_materia_intermedia rmi ON r.id_receta = rmi.id_receta
                        JOIN materia_prima mp ON rmi.id_materia = mp.id_materia
                        JOIN equivalencia AS e ON e.id_receta = r.id_receta
                        GROUP BY g.id_galleta,g.nombre
                ) AS cpg ON cpg.id_galleta = g.id_galleta
            GROUP BY g.id_galleta, g.nombre
            ORDER BY total_merma DESC
            LIMIT 1;
        """)

        # Ejecutar la consulta
        resultadoMerma = db.session.execute(consultaSql5)
        labels_galletaMerma = []
        data_galletaMerma = []
        for venta in resultadoMerma:
            labels_galletaMerma.append(venta.galleta)
            data_galletaMerma.append(venta.total_merma)    

            # Renderizar el template con los datos
            return self.render('ventas.html', 
                            labels_diarias=labels_diarias, data_diarias=data_diarias,
                            labels_semanales=labels_semanales, data_semanales=data_semanales,
                            labels_galletaCostoProduccion=labels_galletaCostoProduccion, data_galletaCostoProduccion=data_galletaCostoProduccion,
                            labels_galletaMasVendida=labels_galletaMasVendida, data_galletaMasVendida=data_galletaMasVendida,
                            labels_galletaUtilidad=labels_galletaUtilidad, data_galletaUtilidad=data_galletaUtilidad,
                            labels_galletaMerma=labels_galletaMerma,data_galletaMerma=data_galletaMerma,
                            solicitudes=datos_solicitudes)





        
admin.add_view(VentasView(name='Análisis de Ventas', menu_icon_type='fa', menu_icon_value='fa-bar-chart', endpoint='ventas'))



@app.route('/ejecutar-consulta-adicional', methods=['POST'])
def ejecutar_consulta_adicional():
    data = request.get_json()  # Obtener los datos JSON enviados en el cuerpo de la solicitud
    inventario_id = data.get('inventario_id')

    try:
        inventario_prod_terminado = db.session.query(InventarioProductoTerminado).filter_by(id_inventario_prod_terminado=inventario_id).first()
        nueva_merma = MermaProdTerminado(
            id_inventario_prod_terminado=inventario_prod_terminado.id_inventario_prod_terminado,
            cantidad=inventario_prod_terminado.cantidad,
            fecha=datetime.now(),
            motivo='Merma caducidad'
        )

        db.session.add(nueva_merma)

        # Actualizar el estatus en el objeto InventarioProductoTerminado
        inventario_prod_terminado.estatus = 0

        # Confirmar la transacción
        db.session.commit()

        return jsonify({'message': 'Consulta adicional ejecutada correctamente'}), 200

    except SQLAlchemyError as e:
        # En caso de que ocurra una excepción de SQLAlchemy, deshacer la sesión y manejar el error
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/consultarStockBajo')
def consulta():
    try:
        query = db.session.query(
                InventarioProductoTerminado.id_galleta,
                Galleta.nombre,
                func.sum(InventarioProductoTerminado.cantidad).label('cantidad')
            ) \
            .join(Galleta, Galleta.id_galleta == InventarioProductoTerminado.id_galleta) \
            .group_by(
                InventarioProductoTerminado.id_galleta,
                Galleta.nombre
            ) \
            .having(func.sum(InventarioProductoTerminado.cantidad) < 10)
            
        results = query.all()
        formatted_results = [{'id_galleta': row.id_galleta, 'nombre': row.nombre, 'cantidad': row.cantidad} for row in results]
        # Devolver los resultados formateados como JSON
        return jsonify(formatted_results), 200
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback any changes made before the exception occurred
        return jsonify({'error': str(e)}), 500
    
@app.route('/consultarGalletasCaducadas')
def consultaCaducadas():
    try:
        # Calcular la fecha dos semanas y un día atrás
        fecha_dos_semanas_un_dia_atras = datetime.now() - timedelta(days=15)

        # Realizar la consulta
        resultados = db.session.query(
                        InventarioProductoTerminado.id_inventario_prod_terminado,
                        InventarioProductoTerminado.id_galleta,
                        InventarioProductoTerminado.fecha_produccion,
                        InventarioProductoTerminado.cantidad,
                        Galleta.nombre
                    )\
                     .join(Galleta, Galleta.id_galleta == InventarioProductoTerminado.id_galleta)\
                     .filter(InventarioProductoTerminado.estatus == 1)\
                     .filter(InventarioProductoTerminado.fecha_produccion <= fecha_dos_semanas_un_dia_atras)
            
        results = resultados.all()

        print(results)

        formatted_results = [{'id_inventario_prod_terminado': row.id_inventario_prod_terminado,'id_galleta': row.id_galleta, 'nombre': row.nombre, 'cantidad': row.cantidad, 'fecha_produccion': row.fecha_produccion} for row in results]
        # Devolver los resultados formateados como JSON
        return jsonify(formatted_results), 200
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback any changes made before the exception occurred
        return jsonify({'error': str(e)}), 500

@app.route('/actualizar_estado', methods=['POST'])
def actualizar_estado():
    data = request.get_json()  # Obtener los datos enviados desde el frontend
    checks_seleccionados = data.get('checks')  # Obtener los valores de los checks seleccionados
    
    try:
        db.session.query(InventarioProductoTerminado).filter(InventarioProductoTerminado.id_inventario_prod_terminado.in_(checks_seleccionados)).update({'estatus': 0}, synchronize_session=False)
        
        # Insertar registros en la tabla "merma_prod_terminado"
        for id_inventario in checks_seleccionados:
            # Obtener el registro de InventarioProductoTerminado
            producto = db.session.query(InventarioProductoTerminado).filter_by(id_inventario_prod_terminado=id_inventario).first()
            # Crear un nuevo registro de MermaProdTerminado
            merma = MermaProdTerminado(
                id_inventario_prod_terminado=id_inventario,
                cantidad=producto.cantidad,
                fecha=datetime.now(),
                motivo='Caducidad'
            )
            db.session.add(merma)
        
        db.session.commit()
        return jsonify({"mensaje": "Los registros fueron actualizados y la merma fue registrada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

class InventarioProductoTerminadoView(ModelView): 
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'      
    def _handle_view(self, name, **kwargs):
        query = db.session.query(
                InventarioProductoTerminado.id_galleta,
                Galleta.nombre,
                func.sum(InventarioProductoTerminado.cantidad).label('cantidad')
            ) \
            .join(Galleta, Galleta.id_galleta == InventarioProductoTerminado.id_galleta) \
            .group_by(
                InventarioProductoTerminado.id_galleta,
                Galleta.nombre
            ) \
            .having(func.sum(InventarioProductoTerminado.cantidad) < 10)
        
        # Ejecutar la consulta y obtener los resultados
        results = query.all()

        if len(results) > 0:
            flash(Markup(f"¡Tienes galletas con stock bajo! <button id='btnStockBajo' class='btn btn-primary'>Ver galletas</button>"), 'warning')

        # Calcular la fecha dos semanas y un día atrás
        fecha_dos_semanas_un_dia_atras = datetime.now() - timedelta(days=15)

        # Realizar la consulta
        resultados = db.session.query(InventarioProductoTerminado, Galleta)\
                     .join(Galleta, Galleta.id_galleta == InventarioProductoTerminado.id_galleta)\
                     .filter(InventarioProductoTerminado.estatus == 1)\
                     .filter(InventarioProductoTerminado.fecha_produccion <= fecha_dos_semanas_un_dia_atras).all()

        if len(resultados) > 0:
            flash(Markup(f"¡Tienes galletas caducadas! <button id='btnGalletasCaducadas' class='btn btn-primary'>Ver galletas</button>"), "error")

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
        permiso = 9
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)

    # Desactivar operaciones de CRUD
    can_create = False
    can_edit = False
    can_delete = False

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)

class GalletaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    porcentaje_ganancia = FloatField('Porcentaje de Ganancia', validators=[DataRequired()])
    imagen = FileUploadField('Imagen', base_path="./src/static/img/galletas")

class GalletaView(ModelView):
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'

    form=GalletaForm
    
    column_list = ('imagen', 'nombre', 'porcentaje_ganancia', 'costo_total_materias_primas', 'precio_final', 'utilidad')

    column_labels = {
        'costo_total_materias_primas': 'Costo Producción',
    }

    def delete_model(self, model):
        """
        Verifica si se puede eliminar una galleta.
        """
        # Verifica si la galleta tiene una relación en la tabla de Receta
        if model.recetas:
            flash("No se puede eliminar la galleta porque tiene una receta asociada.", "error")
            return False

        # Verifica si la galleta tiene una relación en la tabla de InventarioProductoTerminado
        if model.inventarios:
            flash("No se puede eliminar la galleta porque tiene registros en el inventario de producto terminado.", "error")
            return False

        # Si no se encontraron relaciones, se puede eliminar la galleta
        return super().delete_model(model)

    def is_accessible(self):
        permiso = 13
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

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)


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
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'

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

    def tiene_solicitudes_de_produccion(self, receta):
        # Realizar la consulta para contar las solicitudes de producción asociadas a la receta
        count = db.session.query(func.count()).filter(SolicitudProduccion.id_receta == receta.id_receta).scalar()
        
        # Si el recuento es mayor que cero, hay solicitudes de producción asociadas
        return count > 0
    
    def delete_model(self, model):
        """
        Verifica si se puede eliminar una receta.
        """
        # Verificar si hay solicitudes de producción asociadas indirectamente
        # Esto podría ser a través de otras tablas relacionadas
        if self.tiene_solicitudes_de_produccion(model):
            flash("No se puede eliminar la receta porque tiene solicitudes de producción asociadas.", "error")
            return False

        # Si no hay solicitudes de producción asociadas, se puede eliminar la receta
        return super().delete_model(model)

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
    # Si es una operación de creación o edición, actualiza el campo gramaje de la galleta
        if is_created or not is_created:  # Revisa si se está creando o editando el modelo
            # Elimina y reagrega las RecetaMateriaIntermedia relacionadas con la receta
            RecetaMateriaIntermedia.query.filter_by(id_receta=model.id_receta).delete()
            json_materias = json.loads(form.datos_materias_primas.data)  
            for objeto in json_materias:
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
                
            # Calcula el nuevo valor de gramaje para la galleta
            if model.equivalencias and model.equivalencias.piezas != 0:
                nuevo_gramaje_galleta = model.equivalencias.gramaje / model.equivalencias.piezas
            else:
                nuevo_gramaje_galleta = 0
            
            # Actualiza el valor de gramaje en la tabla de galleta asociada
            if model.galleta:
                stmt = (
                    update(Galleta)
                    .where(Galleta.id_galleta == model.id_galleta)
                    .values(gramaje=nuevo_gramaje_galleta)
                )
                db.session.execute(stmt)
            
            # Confirmar los cambios para guardar los objetos en la base de datos
            db.session.commit()
    
    def on_model_delete(self, model):
        # Eliminar las filas asociadas en RecetaMateriaIntermedia
        RecetaMateriaIntermedia.query.filter_by(id_receta=model.id_receta).delete()

        # Confirmar los cambios en la base de datos
        db.session.commit()

        # Llamar al método de eliminación de la clase base para eliminar la receta
        return super().on_model_delete(model)

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)

class MermaProdTerminadoForm(FlaskForm):
    tipo_merma = RadioField('Tipo de merma', choices=[('1', 'Lote'), ('2', 'Individual')], validators=[DataRequired()], default='2', render_kw={"style": "display: inline-block; border: none; list-style: none;"})
    select_galleta_individual = SelectField('Galleta', choices=[], validators=[DataRequired()], coerce=int)
    select_galleta_lote = SelectField('Galleta', choices=[], validators=[DataRequired()], coerce=int)
    cantidad_merma = IntegerField('Cantidad', validators=[NumberRange(min=1)], default=1)
    fecha = DateTimeLocalField('Fecha', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
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

        if self.fecha.data < datetime.now():
            flash('La fecha de merma no puede ser anterior a la fecha y hora actual.', 'warning')
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
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'

    form = MermaProdTerminadoForm
    column_list = ('galleta', 'cantidad', 'fecha', 'motivo')

    column_formatters = {
        'galleta': lambda v, c, m, p: m.inventario_prod_terminado.galleta.nombre if m.inventario_prod_terminado else "Galleta Desconocida"
    }

    def is_accessible(self):
        permiso = 11
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)

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
    
    
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)

class MermaProduccionForm(FlaskForm):
    tipo_merma_materia = RadioField('Tipo de merma', choices=[('1', 'Lote'), ('2', 'Individual')], validators=[DataRequired()], default='2', render_kw={"style": "display: inline-block; border: none; list-style: none;"})
    select_materia_individual = SelectField('Materia Prima', choices=[], validators=[DataRequired()], coerce=int)
    select_materia_lote = SelectField('Materia Prima', choices=[], validators=[DataRequired()], coerce=int)
    cantidad_merma_materia = IntegerField('Cantidad', validators=[NumberRange(min=1), DataRequired()], default=1)
    fecha = DateTimeLocalField('Fecha', format='%Y-%m-%dT%H:%M', validators=[DataRequired(message="Por favor, introduce una fecha.")])
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

        if self.fecha.data < datetime.now():
            flash('La fecha de merma no puede ser anterior a la fecha y hora actual.', 'error')
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
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'
    edit_template = 'admin/traducciones/edit_general.html'

    form = MermaProduccionForm

    column_list = ('id_materia', 'cantidad', 'fecha', 'motivo')

    column_formatters = {
        'id_materia': lambda v, c, m, p: m.materia_prima.nombre if m.materia_prima else "Galleta Desconocida"
    }

    def is_accessible(self):
        permiso = 11
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)

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

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)



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



@app.route('/obtener_costo', methods=['POST'])
def obtener_costo():
    id_producto = request.form.get('id_producto')
    print("idproducto------------------------------------>{}".format(id_producto))
    # Obtén el costo de la materia prima desde la base de datos
    costo = MateriaPrima.query.filter_by(id_materia=id_producto).first().costo
    return jsonify({'costo': costo})










# Define una clase Form personalizada para el formulario de compras
from wtforms import ValidationError
from wtforms.validators import InputRequired, NumberRange

class CompraForm(FlaskForm):
    nombre_producto = SelectField('Nombre del Producto', coerce=int, validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[InputRequired(message="Debe ingresar una cantidad válida."), NumberRange(min=1, message="La cantidad debe ser mayor que cero.")])
    precio_compra = FloatField('Precio de Compra', validators=[InputRequired(message="Debe ingresar un precio válido."), NumberRange(min=0.01, message="El precio debe ser mayor que cero.")])
    fecha_compra = HiddenField('Fecha de Compra')
    fecha_caducidad = DateField('Fecha de Caducidad', validators=[DataRequired()])
    nombre_proveedor = SelectField('Nombre del Proveedor', coerce=int, validators=[DataRequired()])
    costo_oculto = HiddenField('Costo Oculto')
    tipo_medida = SelectField('Tipo de Medida', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(CompraForm, self).__init__(*args, **kwargs)
        self.setup_choices()
        self.setup_default_values()

    
    def setup_choices(self):
        # Consultar los nombres de productos disponibles en la base de datos
        productos = MateriaPrima.query.all()
        # Crear una lista de opciones para el campo de selección de productos
        opciones_productos = [(producto.id_materia, producto.nombre) for producto in productos]
        # Inserta una opción de "elige una opción" como el primer elemento
        opciones_productos.insert(0, (-1, 'Elige una opción'))
        # Establecer las opciones en el campo de selección de productos
        self.nombre_producto.choices = opciones_productos 

        # Consultar los nombres de proveedores disponibles en la base de datos
        proveedores = Proveedor.query.all()
        # Crear una lista de opciones para el campo de selección de proveedores
        opciones_proveedores = [(proveedor.id_proveedor, proveedor.nombre) for proveedor in proveedores]
        # Inserta una opción de "elige una opción" como el primer elemento
        opciones_proveedores.insert(0, (-1, 'Elige una opción'))
        # Establecer las opciones en el campo de selección de proveedores
        self.nombre_proveedor.choices = opciones_proveedores 

          # Consultar los tipos de medida disponibles en la base de datos
        tipos_medida = EquivalenciaMedida.query.all()
        # Crear una lista de opciones para el campo de selección de tipos de medida
        opciones_tipos_medida = [(tipo.id_equivalencia, tipo.unidad) for tipo in tipos_medida]
        # Insertar una opción de "elige una opción" como el primer elemento
        opciones_tipos_medida.insert(0, (-1, 'Elige una opción'))
        # Establecer las opciones en el campo de selección de tipos de medida
        self.tipo_medida.choices = opciones_tipos_medida

    def setup_default_values(self):
        # Establecer la fecha actual como valor predeterminado para la fecha de compra
        self.fecha_compra.data = datetime.today().date()

    def validate_fecha_caducidad(form, field):
        if field.data <= datetime.today().date():
            raise ValidationError('La fecha de caducidad debe ser posterior al día actual.')

    def validate(self):
        if not super(CompraForm, self).validate():
            return False

        # Verificar si se seleccionó una opción válida en el campo de nombre del producto
        if self.nombre_producto.data == -1:
            self.nombre_producto.errors.append('Debes seleccionar un producto.')
            return False

        # Verificar si se seleccionó una opción válida en el campo de nombre del proveedor
        if self.nombre_proveedor.data == -1:
            self.nombre_proveedor.errors.append('Debes seleccionar un proveedor.')
            return False

        # Verificar que la fecha de compra no sea anterior a la fecha actual
        if self.fecha_compra.data < datetime.today().date():
            self.fecha_compra.errors.append('La fecha de compra no puede ser anterior a la fecha actual.')
            return False
    
            
        
        return True

# Define una clase ModelView personalizada para las compras
class CompraView(ModelView):
    create_template = 'admin/traducciones/create_general.html'
    list_template = 'admin/traducciones/list_general.html'  
    edit_template = 'admin/traducciones/edit_general.html'

    form = CompraForm
    column_list = ('nombre_producto', 'cantidad', 'precio_compra', 'fecha_compra', 'fecha_caducidad', 'nombre_proveedor')
    create_template = 'admin/create.html'
 
    def is_accessible(self):
        permiso = 4
        return verificarPermisoUsuario(current_user.id_usuario, permiso, db)


    def on_model_change(self, form, model, is_created):
        # Obtener el nombre del producto seleccionado en el formulario
        id_producto = form.nombre_producto.data
        session['variable'] = True
        nombre_producto = MateriaPrima.query.filter_by(id_materia=id_producto).first().nombre
        
        # Asignar el nombre del producto a la instancia del modelo Compra
        model.nombre_producto = nombre_producto

        # Obtener el nombre del proveedor seleccionado en el formulario
        id_proveedor = form.nombre_proveedor.data
        nombre_proveedor = Proveedor.query.filter_by(id_proveedor=id_proveedor).first().nombre
        
        # Asignar el nombre del proveedor a la instancia del modelo Compra
        model.nombre_proveedor = nombre_proveedor

        # Crear un nuevo registro en la tabla Inventario
        inventario = Inventario(
            id_materia=id_producto,
            cantidad=form.cantidad.data,
            fecha_caducidad=form.fecha_caducidad.data,
            estatus=1,  # El valor de estatus es 1 según lo requerido
            id_proveedor=id_proveedor
        )
        # Agregar el nuevo registro a la sesión
        db.session.add(inventario)

        # Obtener el objeto de materia prima correspondiente al producto comprado
        materia_prima = MateriaPrima.query.get(id_producto)
        prueba = request.cookies.get('pruebas')
        if prueba == 'true':
            total_costo = form.precio_compra.data 
            materia_prima.costo = total_costo
            db.session.commit()
  
      


        












    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Registro guardado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    
    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('El registro no existe.'), 'error')
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Registro modificado exitosamente.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(self.get_url('.edit_view', id=self.get_pk_value(model)))
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """
            Delete model view. Only POST method is allowed.
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()

        if self.validate_form(form):
            # id is InputRequired()
            id = form.id.data

            model = self.get_one(id)

            if model is None:
                flash(gettext('El registro no existe'), 'error')
                return redirect(return_url)

            # message is flashed from within delete_model if it fails
            if self.delete_model(model):
                count = 1
                flash(
                    ngettext('Registro eliminado exitosamente.',
                             '%(count)s registros eliminados exitosamente.',
                             count, count=count), 'success')
                return redirect(return_url)
        else:
            flash_errors(form, message='Ocurrió un error al eliminar el registro. %(error)s')

        return redirect(return_url)



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
    MermaProdTerminadoView(MermaProdTerminado, db.session, menu_icon_type='fa', menu_icon_value="fa-arrow-down", name="Merma Galletas"),
    MermaProduccionView(MermaProduccion, db.session, menu_icon_type='fa', menu_icon_value="fa-thumbs-down", name="Merma Materias"),
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
        if estatus == 0 or estatus == 2:
            ProduccionDAO.actualizarEstatusYFecha(db,idProd,estatusTexto)
        
        #Obtener datos producción & receta-------------------------------------------------
        datosSolicitud, datosReceta = ProduccionDAO.obtenerSolicitudPorID(db, idProd)
        numPiezas = ProduccionDAO.obtenerNumeroPiezasPorReceta(db,datosSolicitud.id_receta)
        #Insertar inventario_producto_terminado
        ProduccionDAO.insertarRegistroInventarioProductoTerminado(db,datosReceta.id_galleta,numPiezas,estatus)
        if estatus == 1:
            respuesta = actualizarInventario(db, datosReceta.id_receta)
            if not respuesta:
                ProduccionDAO.actualizarEstatusYFecha(db,idProd,'Cancelada')
                mensajes_error.append("No existe materia prima suficiente para procesar la solicitud, por lo cual fue cancelada.")
                return jsonify({'errors': mensajes_error})
            else:
                ProduccionDAO.actualizarEstatusYFecha(db,idProd,estatusTexto)
        
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
            if estatus == 0 or estatus == 2:
                ProduccionDAO.actualizarEstatusYFecha(db,idProd,estatusTexto)
            
            #Obtener datos producción & receta-------------------------------------------------
            datosSolicitud, datosReceta = ProduccionDAO.obtenerSolicitudPorID(db, idProd)
            numPiezas = ProduccionDAO.obtenerNumeroPiezasPorReceta(db,datosSolicitud.id_receta)
            #Insertar inventario_producto_terminado
            ProduccionDAO.insertarRegistroInventarioProductoTerminado(db,datosReceta.id_galleta,numPiezas,estatus)
            if estatus == 1:
                respuesta = actualizarInventario(db, datosReceta.id_receta)
                if not respuesta:
                    ProduccionDAO.actualizarEstatusYFecha(db,idProd,'Cancelada')
                    mensajes_error.append("No existe materia prima suficiente para procesar la solicitud, por lo cual fue cancelada.")
                    return jsonify({'errors': mensajes_error})
                else:
                    ProduccionDAO.actualizarEstatusYFecha(db,idProd,estatusTexto)
            
            return jsonify({'exito': 'ok'})
        return self.render('admin/moduloProduccion.html', form=form, modProduccion=modProduccion)

# Registrar la vista de Flask-Admin para tu blueprint produccion_bp
admin.add_view(ProduccionAdminView(name='Produccion', endpoint='produccion_admin', menu_icon_type="fa", menu_icon_value="fa-industry"))

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
            return False
        
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
    return True

def materiaPrimaSuficiente(db, id_receta):
    # Obtener las materias primas requeridas por la receta
    materias_primas_requeridas = ProduccionDAO.obtenerMateriasPrimasPorReceta(db, id_receta)
    for materia_prima in materias_primas_requeridas:
        id_materia = materia_prima.id_materia
        cantidad_requerida = materia_prima.cantidad
        
        # Obtener el inventario de la materia prima ordenado por fecha de caducidad
        inventario = ProduccionDAO.obtenerMateriasPrimasInventario(db, id_materia)
        
        # Verificar si hay suficiente cantidad disponible en el inventario
        cantidad_disponible_total = sum(item.cantidad for item in inventario)
        if cantidad_disponible_total < cantidad_requerida:
            print(f"No hay suficiente cantidad disponible de la materia prima con ID {id_materia}.")
            return False
    return True

@app.route('/obtenerUnidadMedidaMateriaPrima', methods=['GET', 'POST'])
def obtenerUnidadMedidaMateriaPrima():
    materia_id = request.args.get('materia_id')  # Recibe el parámetro de ID de materia
    print("--------------------------------------------{}".format(materia_id))
    # Realiza la consulta y el join
    unidad = MateriaPrimaDAO.obtener_unidad_medida(materia_id)
    return jsonify({'unidad': unidad})



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
    

@app.route('/descargarPDF', methods=["POST"])
def descargarPDF():
    if request.method == "POST":
        pdf_base64 = request.form['pdf_base64']
        pdf_bytes = base64.b64decode(pdf_base64)
        with open("corte_caja.pdf", "wb") as f:
            f.write(pdf_bytes)
        return send_file("corte_caja.pdf", as_attachment=True)

@app.route('/finalizarCorte', methods=["GET", "POST"])
def finalizarCorte():
    
    if request.method == "POST":
        id_corte_caja = request.form['id_corte_caja']
        fecha_de_termino = datetime.now().date()
        hora_termino = datetime.now().time()
        VentaDelDía = 0
        monto_retiro_total = 0
        monto_retiro_total_pago = 0
        
        try:
            CorteCajaDAO.finalizar_corte(id_corte_caja, fecha_de_termino, hora_termino)
            cortes = CorteCajaVentaDAO.consultar_para_generar_corte(id_corte_caja)
            for corte in cortes:
                total = VentaDAO.obtener_total_por_id_venta(int(corte['id_venta']))
                corte['total_venta'] = total
                VentaDelDía += total
            
            retiros = RetiroDAO.consultar_retiros_recolecta_por_id_corte_caja(id_corte_caja)
            for retiro in retiros:
                monto_retiro_total += retiro['monto']
            print(monto_retiro_total)
            print(retiros)

            retiros_pago = RetiroDAO.consultar_retiros_no_recolecta_por_id_corte_caja(id_corte_caja)
            for retiro in retiros_pago:
                monto_retiro_total_pago += retiro['monto']
            print(monto_retiro_total_pago)
            print(retiros_pago)

            pdf_base64 = generar_pdf_corte(cortes, VentaDelDía, retiros, monto_retiro_total, retiros_pago, monto_retiro_total_pago)
            # print(pdf_base64)
            return render_template('ventas/corteCaja.html', cortes=cortes, VentaDelDía=VentaDelDía, retiros=retiros, monto_retiro_total=monto_retiro_total, pdf_base64=pdf_base64, retiros_pago=retiros_pago, monto_retiro_total_pago=monto_retiro_total_pago)
        
        except Exception as ex:
            print("Error al finalizar el corte de caja:", ex)
        
    return render_template('ventas/corteCaja.html')


class VentasPagoView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        galletas = GalletaDAO.get_costo_galletas()
        corte_caja = CorteCajaDAO.consultar_primer_registro_descendente()
        proveedores = ProveedorDAO.consultar_id_nombre_proveedores()
        
        if request.method == "POST":
            proveedor = request.form.get('proveedor')
            monto = request.form.get('cantidadRetiro')
            id_usuario = request.form.get('id_usuario')
            fecha_hora = datetime.now()
            motivo = 'pago a ' + proveedor
            insertar_retiro(id_usuario, monto, fecha_hora, int(corte_caja['id_corte_caja']), motivo)
        
        efectivo_disponible = verificar_efectivo_disponible(int(corte_caja['id_corte_caja']))
        necesita_corte = verificar_corte(int(corte_caja['id_corte_caja']))

        return self.render('ventas/ventas.html', galletas=galletas, corte_caja = corte_caja, necesita_corte=necesita_corte, efectivo_disponible=efectivo_disponible, proveedores=proveedores)
admin.add_view(VentasPagoView(name='VentasRecolecta', endpoint='ventas_pago'))

class VentasRecolectaView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        galletas = GalletaDAO.get_costo_galletas()
        corte_caja = CorteCajaDAO.consultar_primer_registro_descendente()
        proveedores = ProveedorDAO.consultar_id_nombre_proveedores()
        
        if request.method == "POST":
            id_usuario = request.form.get('numero_empleado')
            monto = request.form.get('monto_retirar')
            fecha_hora = datetime.now()
            insertar_retiro(id_usuario, monto, fecha_hora, int(corte_caja['id_corte_caja']), 'recolecta')
        
        efectivo_disponible = verificar_efectivo_disponible(int(corte_caja['id_corte_caja']))
        necesita_corte = verificar_corte(int(corte_caja['id_corte_caja']))

        return self.render('ventas/ventas.html', galletas=galletas, corte_caja = corte_caja, necesita_corte=necesita_corte, efectivo_disponible=efectivo_disponible, proveedores=proveedores)
admin.add_view(VentasRecolectaView(name='VentasRecolecta', endpoint='ventas_recolecta'))

class VentasDiariasView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def ventasCorte(self):
        galletas = GalletaDAO.get_costo_galletas()
        proveedores = ProveedorDAO.consultar_id_nombre_proveedores()
        
        if request.method == "POST":
            id_usuario = request.form.get('numero_empleado')
            fecha_de_inicio = datetime.now().date()
            hora_inicio = datetime.now().time()
            fecha_de_termino = None
            hora_termino = None
            estatus = 0
            id_corte_caja = CorteCajaDAO.insertar_corte_caja(
                fecha_de_inicio, hora_inicio, fecha_de_termino, hora_termino, estatus, id_usuario
            )
            corte_caja = CorteCajaDAO.consultar_primer_registro_descendente()

        else:
            corte_caja = CorteCajaDAO.consultar_primer_registro_descendente()        
        
        efectivo_disponible = verificar_efectivo_disponible(int(corte_caja['id_corte_caja']))
        necesita_corte = verificar_corte(int(corte_caja['id_corte_caja']))

        return self.render('ventas/ventas.html', galletas=galletas, corte_caja = corte_caja, necesita_corte=necesita_corte, efectivo_disponible=efectivo_disponible, proveedores=proveedores)
admin.add_view(VentasDiariasView(name='VentasDiarias', endpoint='ventas_diarias'))

class VenderView(BaseView):
    
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        galletas = GalletaDAO.get_costo_galletas()
        corte_caja = CorteCajaDAO.consultar_primer_registro_descendente()
        efectivo_disponible = verificar_efectivo_disponible(int(corte_caja['id_corte_caja']))
        necesita_corte = verificar_corte(int(corte_caja['id_corte_caja']))
        proveedores = ProveedorDAO.consultar_id_nombre_proveedores()

        if request.method == "POST":
            datos_orden = request.json.get('orden_venta')

            fecha_venta = datetime.now().date()
            hora_venta = datetime.now().time()
            
            try:
                id_venta = insertar_venta(datos_orden, fecha_venta, hora_venta)
                insertar_corte_venta(id_venta, int(corte_caja['id_corte_caja']))
                descontar_inventario(datos_orden)
                pdf_base64 = generar_pdf_ventas(datos_orden, fecha_venta, id_venta)
                
                resultado_venta = {
                    'success': True, 
                    'message': 'Venta registrada exitosamente',
                    'pdf_base64': pdf_base64,  
                    'id_venta': id_venta 
                }

                return jsonify(resultado_venta)
            except Exception as ex:
                resultado_venta = {
                    'success': False, 
                    'message': 'Error al registrar la venta',
                    'error': str(ex)
                }
                return jsonify(resultado_venta)

        return self.render('ventas/ventas.html', galletas=galletas, corte_caja = corte_caja,necesita_corte=necesita_corte, efectivo_disponible = efectivo_disponible, proveedores=proveedores)
        
admin.add_view(VenderView(name='Ventas', endpoint='ventas_admin', menu_icon_type="fa", menu_icon_value="fa-dollar-sign"))
# -------------- INSERTAR RETIRO --------------
def insertar_retiro(id_usuario, monto, fecha_hora, id_corte_caja, motivo):
    try:
        RetiroDAO.insertar_retiro(fecha_hora, monto, motivo,id_corte_caja,id_usuario)
        if motivo == "recolecta":
            CorteCajaVentaDAO.actualizar_estatus(id_corte_caja)
        return 
    except Exception as ex:
        raise Exception(ex)
# -------------- INSERTAR RETIRO --------------

# -------------- EFECTIVO DISPONIBLE --------------
def verificar_efectivo_disponible(id_corte_caja):
    try:
        cortes = CorteCajaVentaDAO.consultar_por_id_corte_caja(id_corte_caja)
        total_ventas = 0 

        for corte in cortes:
            id_venta = corte['id_venta']
            total_venta = VentaDAO.obtener_total_por_id_venta(id_venta)
            total_ventas += total_venta 

        total_ventas = round(total_ventas, 2)

        return total_ventas
    except Exception as ex:
        raise Exception(ex)
# -------------- EFECTIVO DISPONIBLE --------------

# -------------- REQUIERE CORTE --------------
def verificar_corte(id_corte_caja):
    try:
        cortes = CorteCajaVentaDAO.consultar_por_id_corte_caja(id_corte_caja)
        total_ventas = 0 

        for corte in cortes:
            id_venta = corte['id_venta']
            total_venta = VentaDAO.obtener_total_por_id_venta(id_venta)
            total_ventas += total_venta 

        total_ventas = round(total_ventas, 2)

        recolecta = total_ventas > 1000
        resultado = {'dinero_en_caja': total_ventas, 'recolecta': recolecta}

        return resultado
    except Exception as ex:
        raise Exception(ex)
# -------------- REQUIERE CORTE --------------

# -------------- INSERT DE CORTE --------------
def insertar_corte_venta(id_venta, id_corte_caja):
    try:
        corte_caja = CorteCajaDAO.consultar_primer_registro_descendente()
        CorteCajaVentaDAO.insertar_corte_caja_venta(id_venta, id_corte_caja,1)
        
        return
    except Exception as ex:
        raise Exception(ex)
# -------------- INSERT DE CORTE --------------

# -------------- INSERT DE VENTA --------------
def insertar_venta(datos_orden, fecha_venta, hora_venta):
    try:

        subtotal = sum(galleta['costo'] for galleta in datos_orden)
        impuesto = subtotal * 0.16
        total = subtotal + impuesto
        
        id_venta = VentaDAO.insert_venta(fecha_venta, hora_venta, subtotal, total)        

        for galleta in datos_orden:
            id_galleta = galleta['id_galleta']
            medida = galleta['medida']
            cantidad = galleta['cantidad']
            total_detalle = round(galleta['costo'], 2)
            
            if medida == 'gramos' or medida == 'piezas':
                DetalleVentaDAO.insert_detalle_venta(id_venta, id_galleta, medida, cantidad, total_detalle)
            else:
                cantidad_en_gramos = int(medida) * cantidad if medida.isdigit() else 0
                DetalleVentaDAO.insert_detalle_venta(id_venta, id_galleta, 'gramos', cantidad_en_gramos, total_detalle)

        
        return id_venta  
    except Exception as ex:
        raise Exception(ex)
# -------------- INSERT DE VENTA --------------

# -------------- DESCONTAR INVENTARIO --------------
def descontar_inventario(datos_orden):
    try:
        for orden in datos_orden:
            id_galleta = orden['id_galleta']
            medida = orden['medida']
            cantidad = int(orden['cantidad'])
            gramos_por_pieza = float(orden['gramos_por_pieza'])
                
            if medida == 'gramos':
                cantidad = int(cantidad / gramos_por_pieza)
            elif medida == 'piezas':
                pass
            else:
                medida_entero = int(medida)
                cantidad = int(medida_entero * cantidad / gramos_por_pieza)

            registros_mas_antiguos = InventarioProductoTerminadoDAO.obtener_registros_mas_antiguos(id_galleta)

            for registro in registros_mas_antiguos:
                if cantidad <= registro['cantidad']:
                    registro['cantidad'] -= cantidad
                    if registro['cantidad'] == 0:
                        registro['estatus'] = 0
                    InventarioProductoTerminadoDAO.actualizar_registro(registro['id_inventario_prod_terminado'], {'cantidad': registro['cantidad'], 'estatus': registro['estatus']})
                    break
                else:
                    cantidad -= registro['cantidad']
                    registro['cantidad'] = 0
                    registro['estatus'] = 0
                    InventarioProductoTerminadoDAO.actualizar_registro(registro['id_inventario_prod_terminado'], {'cantidad': registro['cantidad'], 'estatus': registro['estatus']})
                    
    except Exception as ex:
        raise Exception(ex)
# -------------- DESCONTAR INVENTARIO --------------

# -------------- GENERACIÓN DEL PDF DE VENTAS--------------
def generar_pdf_ventas(orden_venta, fecha_venta, id_venta):
    subtotal = 0
    
    for galleta in orden_venta:
        subtotal += galleta['costo']

    now = datetime.now()
    pdf_filename = f"ticket_venta_{id_venta}_{fecha_venta}.pdf"
    
    folder_path = os.path.join(os.getcwd(),"tickets_de_venta")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    pdf_path = os.path.join(folder_path, pdf_filename)
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30, title="ticket")
    elements = []

    logo_path = os.path.join(os.getcwd(), 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=100, height=100)
        logo.hAlign = 'LEFT'
        elements.append(logo)
        elements.append(Spacer(1, 20))

    style = getSampleStyleSheet()['Title']
    elements.append(Paragraph("DelightSweets", style))

    data = [["Producto", "Cantidad", "Medida", "Costo"]]
    for galleta in orden_venta:
        medida_texto = galleta['medida']
        if galleta['medida'] not in ['piezas', 'gramos']:
            medida_texto = f"Paquete de {galleta['medida']} gramos"
        data.append([galleta['nombre'], str(galleta['cantidad']), medida_texto, f"${round(galleta['costo'], 2)}"])
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(table)

    elements.append(Paragraph(f"<b>Subtotal:</b> ${round(subtotal, 2)}", style))

    impuesto = round(subtotal * 0.16, 2)
    elements.append(Paragraph(f"<b>Impuesto (16%):</b> ${impuesto}", style))

    total = round(subtotal + impuesto, 2)
    elements.append(Paragraph(f"<b>Total:</b> ${total}", style))

    gracias_style = getSampleStyleSheet()['Normal']

    gracias_style.fontSize = 20
    gracias_style.fontName = 'Helvetica-Bold'
    gracias_style.textColor = colors.brown
    gracias_style.alignment = 1

    elements.append(Paragraph("Gracias por su compra", gracias_style))

    doc.build(elements)

    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

    return pdf_base64

# -------------- GENERACIÓN DEL PDF DE VENTAS --------------

# -------------- GENERACIÓN DEL PDF DE CORTES --------------
def generar_pdf_corte(cortes, venta_del_dia, retiros, monto_retiro_total, retiros_pago, monto_retiro_total_pago):
    now = datetime.now()
    pdf_filename = f"corte_caja_{now.strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    
    folder_path = os.path.join(os.getcwd(), "cortes_de_caja")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    pdf_path = os.path.join(folder_path, pdf_filename)
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30, title="Corte Caja")
    elements = []

    logo_path = os.path.join(os.getcwd(), 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=60, height=60)  
        logo.hAlign = 'LEFT'
        elements.append(logo)
    
    fecha_hora_formato = now.strftime('%d/%m/%Y    hora: %H:%M:%S')
    style = getSampleStyleSheet()['Title']
    elements.append(Paragraph(f"Corte de Caja ( Fecha: {fecha_hora_formato} )", style))
    elements.append(Spacer(1, 20))
    
    data_cortes = [["ID Corte Caja Venta", "ID Venta", "ID Corte Caja", "Total Venta"]]
    for corte in cortes:
        data_cortes.append([
            corte['id_corte_caja_venta'],
            corte['id_venta'],
            corte['id_corte_caja'],
            round(corte['total_venta'], 2)
        ])
    table_cortes = Table(data_cortes)
    table_cortes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(Paragraph("Tabla de Cortes de Caja", style))
    elements.append(table_cortes)
    elements.append(Paragraph(f"Venta del día: ${venta_del_dia:.2f}", style))
    elements.append(Spacer(1, 20))
    
    if retiros:
        data_retiros = [["ID Retiro", "Fecha y Hora", "Monto", "Motivo", "ID Corte Caja", "ID Usuario"]]
        for retiro in retiros:
            data_retiros.append([
                retiro['id_retiro'],
                retiro['fecha_hora'],
                round(retiro['monto'], 2),
                retiro['motivo'],
                retiro['id_corte_caja'],
                retiro['id_usuario']
            ])
        table_retiros = Table(data_retiros)
        table_retiros.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(Paragraph("Tabla de Retiros", style))
        elements.append(table_retiros)
        if monto_retiro_total:
            elements.append(Paragraph(f"Monto Total de Retiros: ${monto_retiro_total:.2f}", style))
        elements.append(Spacer(1, 20))
    
    if retiros_pago:
        data_retiros_pago = [["ID Retiro", "Fecha y Hora", "Monto", "Motivo", "ID Corte Caja", "ID Usuario"]]
        for retiro in retiros_pago:
            data_retiros_pago.append([
                retiro['id_retiro'],
                retiro['fecha_hora'],
                round(retiro['monto'], 2),
                retiro['motivo'],
                retiro['id_corte_caja'],
                retiro['id_usuario']
            ])
        table_retiros_pago = Table(data_retiros_pago)
        table_retiros_pago.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(Paragraph("Tabla de Retiros por Pago", style))
        elements.append(table_retiros_pago)
        if monto_retiro_total_pago:
            elements.append(Paragraph(f"Monto Total de Retiros por Pago: ${monto_retiro_total_pago:.2f}", style))
        elements.append(Spacer(1, 20))

    doc.build(elements)

    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

    return pdf_base64
# -------------- GENERACIÓN DEL PDF DE CORTES --------------


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
