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
# db_user = os.getenv('POSTGRES_USER')
# iam_user = os.getenv('IAM_USER')
# db_password = os.getenv('POSTGRES_PASSWORD')
# db_host = os.getenv('POSTGRES_HOST')
# db_port = os.getenv('POSTGRES_PORT')
# db_database = os.getenv('POSTGRES_DB')
# instance = os.getenv('INSTANCE_CONNECTION_NAME')
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
    # db = create_engine( 'postgresql://postgres:postgres@localhost:5432/IDRL')
    # db = create_engine('postgresql://postgresql:postgresql@localhost:5432/IDRL?client_encoding=utf8')
    conection_string = 'postgresql+psycopg2://{}:{}@{}:{}/{}?client_encoding=utf-8'.format(db_user, db_password, db_host, db_port, db_database)
    db = create_engine(conection_string)
    return db