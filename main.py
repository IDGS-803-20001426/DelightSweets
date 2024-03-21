from flask import Flask,render_template,request,Response
from sqlalchemy import update
from flask_wtf.csrf import CSRFProtect
from flask import redirect
from flask import g
from config import DevelopmentConfig
from flask import flash
import forms

from models import db
from models import Empleados
from models import PedidosPizza
from models import VentasPizzas
from datetime import date

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf=CSRFProtect()

@app.errorhandler(404)
def page_not_fount(e):
    return render_template('404.html'),404


@app.route("/index",methods=["GET","POST"])
def index():    
    emp_form=forms.EmpleadosForm(request.form)
    if request.method=='POST':
        emp=Empleados(nombre=emp_form.nombre.data,
                      correo=emp_form.correo.data,
                      telefono=emp_form.telefono.data,
                      direccion=emp_form.direccion.data,
                      sueldo=emp_form.sueldo.data)
        db.session.add(emp)
        db.session.commit()
    return render_template("index.html",form=emp_form)

@app.route('/modificar', methods=["GET","POST"])
def modificar():
    emp_form=forms.EmpleadosForm(request.form)
    if request.method=='GET':
        id=request.args.get('id')
        emp1=db.session.query(Empleados).filter(Empleados.id==id).first()
        emp_form.id.data=request.args.get('id')
        emp_form.nombre.data=emp1.nombre
        emp_form.correo.data=emp1.correo
        emp_form.telefono.data=emp1.telefono
        emp_form.direccion.data=emp1.direccion
        emp_form.sueldo.data=emp1.sueldo
    if request.method=='POST':
        id=emp_form.id.data
        emp1=db.session.query(Empleados).filter(Empleados.id==id).first()
        emp1.nombre=emp_form.nombre.data
        emp1.nombre=emp_form.nombre.data
        emp1.correo=emp_form.correo.data
        emp1.telefono=emp_form.telefono.data
        emp1.telefono=emp_form.telefono.data
        emp1.direccion=emp_form.direccion.data
        emp1.sueldo=emp_form.sueldo.data
        db.session.add(emp1)
        db.session.commit()
        return redirect('ABC_Completo')
    return render_template("modificar.html", form=emp_form)

@app.route('/eliminar', methods=["GET","POST"])
def eliminar():
    emp_form=forms.EmpleadosForm(request.form)
    if request.method=='GET':
        id=request.args.get('id')
        emp1=db.session.query(Empleados).filter(Empleados.id==id).first()
        emp_form.id.data=request.args.get('id')
        emp_form.nombre.data=emp1.nombre
        emp_form.correo.data=emp1.correo
        emp_form.telefono.data=emp1.telefono
        emp_form.direccion.data=emp1.direccion
        emp_form.sueldo.data=emp1.sueldo
        
    if request.method=='POST':
        id=emp_form.id.data
        alum=Empleados.query.get(id)
        db.session.delete(alum)
        db.session.commit()
        return redirect('ABC_Completo')
    return render_template("eliminar.html", form=emp_form)
        

@app.route("/ABC_Completo",methods=["GET","POST"])
def ABC_Completo():
    
    empleado=Empleados.query.all()
    return render_template("ABC_Completo.html", empleados=empleado)


ingredientesDiccionario = {
    '1': 'Jamon',
    '2': 'Piña',
    '3': 'Champiñones'
}
tamañoDiccionario = {
    '40': 'Chica',
    '80': 'Mediana',
    '120': 'Grande'
}

mismaVenta = True
nombreCliente = ""
direccionCliente = ""
telefonoCliente = ""

@app.route("/pizzeria",methods=["GET","POST"])
def pizzeria():
    global mismaVenta
    global nombreCliente
    global direccionCliente
    global telefonoCliente

    pizzeria_form=forms.PizzeriaForm(request.form)
    formFecha = forms.ConsultaPedidosForm(request.form)
    pedidosPiza = PedidosPizza.query.filter_by(estatus=1).all()

    if request.method == 'POST' and pizzeria_form.validate():
        jamon=pizzeria_form.jamon.data
        piña=pizzeria_form.piña.data
        champiñones=pizzeria_form.champiñones.data
        costoIngredientes = 0
        lstIngresientes = ''
        if jamon:
            costoIngredientes += 10
            lstIngresientes += '1,'
        if piña:
            costoIngredientes += 10
            lstIngresientes += '2,'
        if champiñones:
            costoIngredientes += 10
            lstIngresientes += '3,'            
        
        costoPizza = int(pizzeria_form.tamaPizza.data)
        totalPizza = int(pizzeria_form.numPizzas.data)
        subtotalPizza = str( (costoPizza+costoIngredientes)*totalPizza )
        totalPizza = "0"
        
        numVenta = db.session.query(db.func.max(PedidosPizza.numeroVenta)).scalar()
        if numVenta is None:
            numVenta = 1
        elif mismaVenta:
            nombreCliente = pizzeria_form.nombre.data
            direccionCliente = pizzeria_form.direccion.data
            telefonoCliente = pizzeria_form.telefono.data

            pizzeria_form.nombre.data = nombreCliente
            pizzeria_form.direccion.data = direccionCliente
            pizzeria_form.telefono.data = telefonoCliente

            pizzeria_form.nombre.render_kw = {'readonly': True}
            pizzeria_form.direccion.render_kw = {'readonly': True}
            pizzeria_form.telefono.render_kw = {'readonly': True}
            pass
        else:
            numVenta = str(int(numVenta)+1)
            pizzeria_form.nombre.render_kw = {'readonly': False}
            pizzeria_form.direccion.render_kw = {'readonly': False}
            pizzeria_form.telefono.render_kw = {'readonly': False}
            mismaVenta = True                

        nuevo_pedido = PedidosPizza(
            nombre=pizzeria_form.nombre.data,
            direccion=pizzeria_form.direccion.data,
            telefono=pizzeria_form.telefono.data,
            tamaPizza=pizzeria_form.tamaPizza.data,
            ingredientesPizza=lstIngresientes,
            numPizza=pizzeria_form.numPizzas.data,
            subtotal=subtotalPizza,
            total=totalPizza,
            numeroVenta = numVenta,
            estatus = "1",
            create_date=pizzeria_form.fecha.data
        )
        db.session.add(nuevo_pedido)
        db.session.commit()
        pedidosPiza = PedidosPizza.query.filter_by(estatus=1).all()
        for pedido in pedidosPiza:
            if pedido.ingredientesPizza:
                ingredientes = pedido.ingredientesPizza.split(',')  
                ingredientes_texto = ', '.join([ingredientesDiccionario.get(ingrediente, '') for ingrediente in ingredientes])
                pedido.ingredientesPizza = ingredientes_texto
            pedido.tamaPizza = tamañoDiccionario.get(pedido.tamaPizza, '')


        return render_template("pizzeria.html",pedidos=pedidosPiza,form=pizzeria_form, formF=formFecha)
        
    fecha_seleccionada = formFecha.fecha_seleccionada.data
    if not fecha_seleccionada: 
        fecha_seleccionada = date.today()  
    ventasFecha = db.session.query(VentasPizzas.nombre, db.func.sum(VentasPizzas.total).label('total')).filter(VentasPizzas.create_date == fecha_seleccionada).group_by(VentasPizzas.nombre).all()
    print(ventasFecha)
    for pedido in pedidosPiza:
        if pedido.ingredientesPizza:
            ingredientes = pedido.ingredientesPizza.split(',')
            ingredientes_texto = ', '.join([ingredientesDiccionario.get(ingrediente, '') for ingrediente in ingredientes])
            pedido.ingredientesPizza = ingredientes_texto
        pedido.tamaPizza = tamañoDiccionario.get(pedido.tamaPizza, '')

    return render_template("pizzeria.html",pedidos=pedidosPiza,form=pizzeria_form,formF=formFecha,ventasFecha=ventasFecha)

@app.route("/modificarPedido",methods=["GET","POST"])
def modificarPedido():
    pizzeria_form=forms.PizzeriaForm(request.form)
    if request.method == 'GET':
        id=request.args.get('id')
        pedidoPizza= db.session.query(PedidosPizza).filter(PedidosPizza.id==id).first()
        pizzeria_form.id.data = request.args.get('id')
        pizzeria_form.nombre.data=pedidoPizza.nombre
        pizzeria_form.direccion.data=pedidoPizza.direccion
        pizzeria_form.telefono.data=pedidoPizza.telefono 
        pizzeria_form.fecha.data=pedidoPizza.create_date
        pizzeria_form.tamaPizza.data=pedidoPizza.tamaPizza
        pizzeria_form.numPizzas.data=pedidoPizza.numPizza
        pizzeria_form.fecha.data=pedidoPizza.create_date
        
        # Separar los ingredientes por comas
        ingredientes = pedidoPizza.ingredientesPizza.split(',')
        for ingrediente in ingredientes:
            if ingrediente == '1':
                pizzeria_form.jamon.data = True
            elif ingrediente == '2':
                pizzeria_form.piña.data = True
            elif ingrediente == '3':
                pizzeria_form.champiñones.data = True
    if request.method == 'POST':
        jamon=pizzeria_form.jamon.data
        piña=pizzeria_form.piña.data
        champiñones=pizzeria_form.champiñones.data
        costoIngredientes = 0
        lstIngresientes = ''
        if jamon:
            costoIngredientes += 10
            lstIngresientes += '1,'
        if piña:
            costoIngredientes += 10
            lstIngresientes += '2,'
        if champiñones:
            costoIngredientes += 10
            lstIngresientes += '3,'

        id=pizzeria_form.id.data
        pedidoPizza1= db.session.query(PedidosPizza).filter(PedidosPizza.id==id).first()
        pedidoPizza1.nombre=pizzeria_form.nombre.data
        pedidoPizza1.direccion=pizzeria_form.direccion.data
        pedidoPizza1.telefono=pizzeria_form.telefono.data
        pedidoPizza1.create_date=pizzeria_form.fecha.data
        pedidoPizza1.tamaPizza =pizzeria_form.tamaPizza.data
        pedidoPizza1.ingredientesPizza=lstIngresientes
        pedidoPizza1.numPizza=pizzeria_form.numPizzas.data
        pedidoPizza1.create_date = pizzeria_form.fecha.data

        costoPizza = int(pizzeria_form.tamaPizza.data)
        totalPizza = int(pizzeria_form.numPizzas.data)
        subtotalPizza = str( (costoPizza+costoIngredientes)*totalPizza )
        totalPizza = "0"

        pedidoPizza1.subtotal = subtotalPizza
        pedidoPizza1.total = totalPizza

        db.session.add(pedidoPizza1)
        db.session.commit()
        return redirect('pizzeria')
    return render_template("modificarPedido.html",form=pizzeria_form)

@app.route("/eliminarPedido", methods=["POST"])
def eliminarPedido():
    if request.method == 'POST':
        ids_seleccionados = request.form.getlist('pedidos_seleccionados')
        for id_pedido in ids_seleccionados:
            pedido = PedidosPizza.query.get(id_pedido)
            if pedido:
                db.session.delete(pedido)
                db.session.commit()        
        return redirect('pizzeria')
    
@app.route("/terminarPedido", methods=["POST"])
def terminarPedido():
    if request.method == 'POST':
        global mismaVenta
        max_id = db.session.query(db.func.max(PedidosPizza.numeroVenta)).scalar()
        suma_subtotal = db.session.query(db.func.sum(PedidosPizza.subtotal)).filter(PedidosPizza.numeroVenta == max_id).scalar()
        mismaVenta = False
        nombreCliente = db.session.query(PedidosPizza.nombre).filter(PedidosPizza.numeroVenta == max_id).first()[0]
        fechaVenta = db.session.query(PedidosPizza.create_date).filter(PedidosPizza.numeroVenta == max_id).first()[0]
        
        print('-------------------LA FECHA ES: {}'.format(fechaVenta))

        nuevaVenta = VentasPizzas(
            nombre=nombreCliente,
            numeroVenta=max_id,
            total=suma_subtotal,
            create_date = fechaVenta
        )
        db.session.add(nuevaVenta)
        db.session.commit()

        stmt = update(PedidosPizza).where(PedidosPizza.numeroVenta == max_id).values(estatus=0)
        db.session.execute(stmt)
        db.session.commit()
        mismaVenta = False

        return redirect('pizzeria')

@app.route("/pedidosFecha", methods=["POST"])
def pedidosFecha():
    formFecha = forms.ConsultaPedidosForm(request.form)
    pizzeria_form = forms.PizzeriaForm(request.form)
    fecha_seleccionada = formFecha.fecha_seleccionada.data
    dia = formFecha.dias_semana.data
    mes = formFecha.meses.data
    anio = formFecha.anios.data

    print(fecha_seleccionada)
    print(dia)
    print(mes)
    print(anio)

    if not fecha_seleccionada and not dia and not mes and not anio:
        fecha_seleccionada = date.today()
    ventasFecha={}
    if fecha_seleccionada:
        # print("FECHA")
        ventasFecha = db.session.query(
            VentasPizzas.nombre,
            db.func.sum(VentasPizzas.total).label('total')
        ).filter(
            VentasPizzas.create_date == fecha_seleccionada
        ).group_by(
            VentasPizzas.nombre
        ).all()
    elif dia:
        dia_mysql = {
            0: 2,  
            1: 3,  
            2: 4,  
            3: 5,  
            4: 6,  
            5: 7,  
            6: 1   
        }
        
        dia_mysql = dia_mysql[int(dia)]

        ventasFecha = db.session.query(
            VentasPizzas.nombre,
            db.func.sum(VentasPizzas.total).label('total')
        ).filter(
            db.func.DAYOFWEEK(VentasPizzas.create_date) == dia_mysql
        ).group_by(
            VentasPizzas.nombre
        ).all()

    elif mes:
        print("mes")
        ventasFecha = db.session.query(
            VentasPizzas.nombre,
            db.func.sum(VentasPizzas.total).label('total')
        ).filter(
            db.func.extract('month', VentasPizzas.create_date) == mes
        ).group_by(
            VentasPizzas.nombre
        ).all()
    elif anio:
        print("año")
        ventasFecha = db.session.query(
            VentasPizzas.nombre,
            db.func.sum(VentasPizzas.total).label('total')
        ).filter(
            db.func.extract('year', VentasPizzas.create_date) == anio
        ).group_by(
            VentasPizzas.nombre
        ).all()
    
    print(ventasFecha)
    sumatotal = 0
    for ven in ventasFecha: 
        print(ven.total)
        sumatotal += ven.total

    return render_template("pizzeria.html", sumatotal = sumatotal, formF=formFecha, ventasFecha=ventasFecha, form=pizzeria_form)
    

# @app.route("/alumnos",methods=["GET","POST"])
# def alum():
#     nom=""
#     apa=""
#     ama=""
#     mensaje = ""
#     alum_form=forms.UsersForm(request.form)
#     if request.method=='POST' and alum_form.validate():
#         nom=alum_form.nombre.data
#         apa=alum_form.apaterno.data
#         ama=alum_form.amaterno.data

#         mensaje = 'Bienvenido {}'.format(nom)
#         flash(mensaje)

#         print("NOMBRE: {}".format(nom))
#         print("APATERNO: {}".format(apa))
#         print("AMATERNO: {}".format(ama))

#     return render_template("alumnos.html", form=alum_form, nom=nom, apa=apa, ama=ama)

if __name__=="__main__":
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()
    