from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required,current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.base import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash


# Models:
from models.Models import User,db,Rol
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
    def is_accessible(self):
        return current_user.is_authenticated
        
admin = Admin(
    app,
    name='Panel Administrador',  # Nombre personalizado para el panel de administración
    base_template='layoutMaster.html',  # Plantilla base personalizada
    template_mode='bootstrap3'  # Modo de plantilla (en este caso, Bootstrap 5)
)


class UserView(MyModelView):
    column_exclude_list = ('contrasenia')  # Exclude password from the list view
    form_excluded_columns = ()  # Exclude password from the edit/create form

    def on_model_change(self, form, model, is_created):
        # Generate password hash before saving the user
        if 'contrasenia' in form.data and form.data['contrasenia']:
            model.contrasenia = generate_password_hash(form.data['contrasenia'])
  

    
# # Add views to admin
admin.add_view(UserView(User,db.session,name="usuarios"))


@app.route('/admin')
@login_required  # Asegura que solo los usuarios autenticados puedan acceder
def admin_panel():
    return redirect('/admin/')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # print(request.form['username'])
        # print(request.form['password'])
        user = Usuario(0, request.form['username'], request.form['password'])
        logged_user = UserDAO.login(user)
        return validarInicioSesion(logged_user)
    else:
        return render_template('auth/login.html')

def validarInicioSesion(logged_user):
    if logged_user != None:
        if logged_user.contrasenia:
            login_user(logged_user)
            return redirect(url_for('home'))
        else:
            flash("Invalid password...")
            return render_template('auth/login.html')
    else:
        flash("User not found...")
        return render_template('auth/login.html')

@app.route('/home')
def home():
    print("tipo Usuario {} ".format(current_user.rol))
    if current_user.rol == 1:  
        return redirect('/admin')
    else:
        return render_template('home.html')


@app.route('/ventas')
def ventas():
    return render_template('ventas/ventas.html')

@app.route('/protected')
@login_required
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"

#Cerrar Sesión --------------------------------------------------
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
#Errores de búsqueda --------------------------------------------
def status_401(error):
    return render_template('errores/401.html'),401

def status_404(error):
    return render_template('errores/404.html'),404
#----------------------------------------------------------------

if __name__ == '__main__':
    csrf.init_app(app)
    db.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    with app.app_context():
        db.create_all()
    app.run()
