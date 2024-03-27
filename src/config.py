import os 
from sqlalchemy import create_engine
from sqlalchemy import update
import urllib

# Se necesitainstalar estas cosas
# pip install SQLAlchemy
# pip install Flask-SQLAlchemys
# pip install PyMySQL
class Config(object):
    SECRET_KEY= 'B!1w8NAt1T^%kvhUI*S^'
    SESSION_COOKIE_SECURE= False
class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:@127.0.0.1/proyectogalleta'
    SQLALCHEMY_TRACK_MODIFICATIONS=False

config = {
    'development': DevelopmentConfig
}
