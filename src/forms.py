from wtforms import Form
from wtforms import StringField,SelectField,RadioField,EmailField,IntegerField,DateField,BooleanField,DecimalField
from wtforms import validators
from wtforms.validators import DataRequired


class ProduccionModificarForm(Form):
    id = IntegerField('id_solicitud')
    estatusProduccion = SelectField('Estatus', 
        choices=[('', 'Seleccione un estatus'), 
                (0, 'Solicitada'),
                (1, 'Terminada'),
                (2, 'Cancelada')
            ])

class OrdenVentaForm(Form):
    id_galleta = IntegerField('ID Galleta')
    nombre = StringField('Galleta')
    medida = SelectField('Medida', choices=[('gramos', 'Gramos'), ('piezas', 'Piezas')])
    cantidad = IntegerField('Cantidad')
    precio = DecimalField('Precio')
