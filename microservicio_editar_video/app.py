from celery import Celery
from modelos import db, Video, VideoSchema
from sqlalchemy.orm import sessionmaker
from flask import Flask,request
import configparser
import base64

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

file_upload_dir = config['Paths']['file_upload_dir']

# Crear la aplicación
def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/IDRL'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

app = create_app('default')
app_context = app.app_context()
app_context.push()

Session = sessionmaker(bind=db)
session = Session()

celery_app = Celery(__name__, broker='redis://localhost:6379/0')
@celery_app.task(name='edit_video')
def edit_video(*args):
    with app.app_context():
        video_schema = VideoSchema()
        print(args)
        video = session.query(Video).get(args[0])

        if video is None:
            return '', 404

        file_name = args[1]
        file_dir = file_upload_dir + "\\" + "edited_" + file_name
        fh = open(file_dir, "wb")
        fh.write(base64.b64decode(args[2]))
        fh.close()

        video.status = "PROCESADO"
        video.edited = file_dir
        session.commit()
        return video_schema.dump(video), 200