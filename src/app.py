from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required,current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.base import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash


# Models:
from models.Models import User,db,Rol,Galleta
from models.entities.User import Usuario
from models.usersDao import UserDAO
from models.galletaDao import GalletaDAO,DetalleVentaDAO,VentaDAO,InventarioProductoTerminadoDAO
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


@app.route('/ventas', methods=["GET", "POST"])
def ventas():
    galletas = GalletaDAO.get_costo_galletas()
    # print(galletas)
    orden_venta = []
    
    if request.method == "POST":
        datos_orden = request.json.get('orden_venta')
        # print(datos_orden)

        fecha_venta = datetime.now().date()
        hora_venta = datetime.now().time()
        
        try:
            id_venta = insertar_venta(datos_orden, fecha_venta, hora_venta)
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
    
    return render_template('ventas/ventas.html', galletas=galletas, orden=orden_venta)

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

# -------------- GENERACIÓN DEL PDF --------------
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
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
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

# -------------- GENERACIÓN DEL PDF --------------


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
