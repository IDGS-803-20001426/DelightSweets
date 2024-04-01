from wtforms import Form, StringField, SelectField, IntegerField, DecimalField

class OrdenVentaForm(Form):
    id_galleta = IntegerField('ID Galleta')
    nombre = StringField('Galleta')
    medida = SelectField('Medida', choices=[('gramos', 'Gramos'), ('piezas', 'Piezas')])
    cantidad = IntegerField('Cantidad')
    precio = DecimalField('Precio')
