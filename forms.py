from wtforms import Form
from wtforms import StringField,SelectField,RadioField,EmailField,IntegerField,DateField,BooleanField
from wtforms import validators
from wtforms.validators import DataRequired


class UsersForm(Form):
    nombre=StringField('nombre',[
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=4, max=10, message='ingrese nombre valido')
    ])
    apaterno=StringField('apaterno',[
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=4, max=10, message='ingrese apellido valido')
    ])
    amaterno=StringField('amaterno',[
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=4, max=10, message='ingrese apellido valido')
    ])

    edad=IntegerField('edad',[        
        validators.number_range(min=1, max=20,message='ingrese edad valida')
    ])
    correo=StringField('correo',[
        validators.DataRequired(message='el campo es requerido'),
    ])

    # nombre=StringField('nombre')
    # apaterno=StringField('apaterno')
    # amaterno=StringField('amaterno')
    # edad=IntegerField('edad')
    # correo=EmailField('correo')

class EmpleadosForm(Form):
    id=IntegerField('id')
    nombre=StringField('nombre',[
        validators.DataRequired(message='el campo es requerido'),
        validators.length(min=4, max=10, message='ingrese nombre valido')
    ])
    correo=StringField('correo',[
        validators.DataRequired(message='ingresar un correo valido'),
    ])
    telefono=StringField('telefono')
    direccion=StringField('direccion')
    sueldo=StringField('sueldo')
    

class PizzeriaForm(Form):
    id = IntegerField('id')
    nombre= StringField('nombre',[
        validators.DataRequired(message='el campo es requerido')
    ])
    direccion= StringField('direccion',[
        validators.DataRequired(message='el campo es requerido')
    ])
    telefono= StringField('telefono',[
        validators.DataRequired(message='el campo es requerido')
    ])
    fecha = DateField('Seleccione una fecha', validators=[DataRequired()], format='%Y-%m-%d')

    numPizzas = IntegerField('Número Pizzas', [
        validators.DataRequired(message='El campo es requerido'),
        validators.NumberRange(min=1, message='El número de pizzas no puede ser negativo')
    ])    
    tamaPizza = RadioField('Tamaño Pizza', 
       choices=[
            ('40','Chica $40'),
            ('80','Mediana $80'),
            ('120','Grande $120')
            ])
    
    # ingredientesPizza = RadioField('Ingredientes Pizza', 
    #    choices=[
    #         ('1','Jamon $10'),
    #         ('2','Piña $10'),
    #         ('3','Champiñones $10')
    #         ])
    
    jamon = BooleanField('Jamon $10', default=False)
    piña = BooleanField('Piña $10', default=False)
    champiñones = BooleanField('Champiñones $10', default=False)

    numVenta = StringField('numVenta')
    estatus= StringField('Estatus')
    subtotal= StringField('Subtotal')
    total= StringField('Total')


class ConsultaPedidosForm(Form):
    fecha_seleccionada = DateField(format='%Y-%m-%d')

    dias_semana = SelectField('Filtrar por día de la semana', choices=[('', 'Seleccione un día'), (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')])

    meses = SelectField('Filtrar por mes', choices=[('', 'Seleccione un mes'), (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'), (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'), (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')])

    anios = SelectField('Filtrar por año', choices=[('', 'Seleccione un año'), (2020, '2020'), (2021, '2021'), (2022, '2022'), (2023, '2023'), (2024, '2024')])