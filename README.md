# Crear Base de Datos 
- proyectoGalleta
    - CREATE DATABASE proyectoGalleta;
# Crear Usuario diferente al root
- Crear un usuario
    - CREATE USER 'donGalleta'@'localhost' IDENTIFIED WITH mysql_native_password BY 'proyecto';
- Asignar permisos al usuario
    - GRANT SELECT, INSERT, UPDATE ON proyectGalleta.* TO 'donGalleta'@'localhost';
- Permite ver los permisos
    - SHOW GRANTS FOR 'donGalleta'@'localhost';
# Instalar las dependencias
- python -m venv .env
- pip install -r requirements.txt
- pip install flask flask-login flask-mysqldb flask-WTF
# Ejecutar la aplicación
- py .\src\app.py

# Login Requerido
- @login_required
  - Deben de agregarlo después de su ruta, si no cuentan con un inicio de sesicón les mandara error 401.

  