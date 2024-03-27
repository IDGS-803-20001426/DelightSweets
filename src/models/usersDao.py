from .Models import User

class UserDAO:

    @classmethod
    def login(cls, user):
        try:

            username = user.nombre_usuario
            password = user.contrasenia
            print(username)
            print(password)
            
            user_from_db = User.query.filter_by(nombre_usuario=username).first()
            if user_from_db and User.check_password(user_from_db.contrasenia, password):
                return user_from_db
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(cls, id_usuario):
        try:
            return User.query.get(id_usuario)
        except Exception as ex:
            raise Exception(ex)
