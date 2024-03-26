from .Models import User

class UserDAO:

    @classmethod
    def login(cls, user):
        try:
            username = user.username
            password = user.password
            user_from_db = User.query.filter_by(username=username).first()
            if user_from_db and User.check_password(user_from_db.password, password):
                return user_from_db
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(cls, user_id):
        try:
            return User.query.get(user_id)
        except Exception as ex:
            raise Exception(ex)
