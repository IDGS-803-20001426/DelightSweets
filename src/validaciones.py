from wtforms import StringField,PasswordField
from wtforms.validators import DataRequired, Length, Regexp
from models.usersDao import UserDAO
from werkzeug.security import generate_password_hash,check_password_hash
import re

# Define la función validar_palabras_consulta---------------------------------------------------------------------
def validarPalabrasConsulta(form_class, campos):
    palabras_consulta = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
    for campo in campos:
        setattr(form_class, campo, StringField(validators=[DataRequired(), Regexp(
            rf'^(?!.*({"|".join(palabras_consulta)})\b)',
            message=f"No se permiten palabras de consulta en el campo ."
        )]))

def validarFormulario(form_class, campos):
    palabras_consulta = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
    palabras_restringidas = ['<script', '</script>', '<style', '</style>']
    for campo in campos:
        setattr(form_class, campo, StringField(validators=[DataRequired(), Regexp(
            r'^[^<>\[\]!@#$%^&*()_+`~{}|\\]+$',  # Expresión regular que permite cualquier texto excepto caracteres especiales
            message=f"No se permiten caracteres especiales en el campo {campo}."
        ), Regexp(
            r'^[^<>\[\]]+$',  # Expresión regular que permite cualquier texto excepto '<', '>', '[', o ']'
            message=f"No se permiten etiquetas HTML en el campo {campo}."
        ), Regexp(
            rf'^(?!.*({"|".join(palabras_restringidas)})\b)',
            message=f"No se permiten las palabras 'script' o 'style' en el campo {campo}."
        ), Regexp(
            rf'^(?!.*({"|".join(palabras_consulta)})\b)',
            message=f"No se permiten palabras de consulta en el campo {campo}."
        )]))

def validarContrasenia(form_class, campo):
    contrasenias_comunes = cargarContraseñasComunes()
    
    # Define la función de validación personalizada
    def _validate(form, field):
        if field.data in contrasenias_comunes:
            form.contrasenia.errors.append("La contraseña ingresada es común.")

    setattr(form_class, campo, PasswordField(validators=[DataRequired(), Regexp(
        r'^(?=.*[a-z])(?=.*[A-Z])[a-zA-Z\d]+$',
        message="La contraseña debe contener al menos una mayúscula, una minúscula y no debe contener caracteres especiales."
    ), Regexp(
        r'^[^<>\[\]!@#$%^&*()_+`~{}|\\]+$',  # Expresión regular que permite cualquier texto excepto caracteres especiales
        message="La contraseña no debe contener caracteres especiales."
    ), Regexp(
        r'^[^<>\[\]]+$',  # Expresión regular que permite cualquier texto excepto '<', '>', '[', o ']'
        message="La contraseña no debe contener etiquetas HTML."
    ), Regexp(
        r'^(?!.*<script\b)(?!.*<\/script\b)(?!.*<style\b)(?!.*<\/style\b)',
        message="La contraseña no debe contener las palabras 'script' o 'style'."
    ), Regexp(
        r'^(?!.*SELECT\b)(?!.*INSERT\b)(?!.*UPDATE\b)(?!.*DELETE\b)',
        message="La contraseña no debe contener palabras de consulta como 'SELECT', 'INSERT', 'UPDATE' o 'DELETE'."
    ),
    _validate
    
    ]))


def cargarContraseñasComunes():
    contrasenias_comunes = set()
    with open('src/contras.txt', 'r') as file:
        for line in file:
            contrasenias_comunes.add(line.strip())
    return contrasenias_comunes

def validarCamposLogin(username, password):
    validarCaracteresEspeciales = re.compile(r'[!@#$%^&*(),.?":{}|<>]')
    validarConsultasSQL = re.compile(r'\b(?:INSERT|SELECT|UPDATE|DROP|DELETE|UNION|JOIN)\b', re.IGNORECASE)

    # Validar username
    if validarCaracteresEspeciales.search(username) or validarConsultasSQL.search(username):
        return False
    # Validar password
    if validarCaracteresEspeciales.search(password) or validarConsultasSQL.search(password):
        return False
    return True

# ----------------------------------------------------------------------------------------------------