import os
from sqlalchemy import create_engine
from sqlalchemy import update
import urllib

class Config(object):
    SECRET_KEY='Clave_nueva'
    SESSION_COOKIE_SECURE=False


class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:@127.0.0.1/pruebasbdidgs803'
    SQLALCHEMY_TRACK_MODIFICATIONS=False
