from flask import Flask
from sqlalchemy import create_engine

# Crear la aplicación
def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/IDRL'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

# Crear la base de datos
def create_db():
    # db = create_engine( 'postgresql://postgres:postgres@localhost:5432/IDRL')
    # db = create_engine('postgresql://postgresql:postgresql@localhost:5432/IDRL?client_encoding=utf8')
    conection_string = 'postgresql+psycopg2://{}:{}@{}:{}/{}?client_encoding=utf-8'.format("postgres", "postgresql", "localhost", "5432", "IDRL")
    db = create_engine(conection_string)
    return db