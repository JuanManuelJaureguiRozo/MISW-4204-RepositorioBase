from flask import Flask
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import configparser

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

db_user = config['credentials']['db_user']
db_password = config['credentials']['db_password']
db_host = config['credentials']['db_host']
db_port = config['credentials']['db_port']
db_database = config['credentials']['db_database']

load_dotenv()
db_user = config['credentials']['db_user']
db_password = config['credentials']['db_password']
db_host = config['credentials']['db_host']
db_port = config['credentials']['db_port']
db_database = config['credentials']['db_database']

# Crear la aplicación
def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/IDRL'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

# Crear la base de datos
def create_db():
    conection_string = 'postgresql+psycopg2://{}:{}@{}:{}/{}?client_encoding=utf-8'.format(db_user, db_password, db_host, db_port, db_database)
    db = create_engine(conection_string)
    return db