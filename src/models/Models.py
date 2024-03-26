from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

class User(db.Model,UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(200))
    fullname = db.Column(db.String(100))
    tipoUsuario = db.Column(db.Integer)
    statusUsuario = db.Column(db.Integer)
    create_date = db.Column(db.DateTime, default=datetime.datetime.now)

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)