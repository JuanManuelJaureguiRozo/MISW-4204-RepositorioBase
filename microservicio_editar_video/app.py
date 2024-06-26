from celery import Celery
from modelos import db, Video, VideoSchema
from sqlalchemy.orm import sessionmaker
from flask import Flask,request
import configparser
import cv2 as cv2
from moviepy.editor import VideoFileClip, concatenate_videoclips,CompositeVideoClip
import base64

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

file_upload_dir = config['Paths']['file_upload_dir']
file_logo_dir = config['Paths']['file_logo_dir']

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
        # print(args)
        task_video = session.query(Video).get(args[0])

        if task_video is None:
            return '', 404

        file_name = args[1]
        file_dir = file_upload_dir + "\\" + "edited_" + file_name
        fh = open(file_dir, "wb")
        fh.write(base64.b64decode(args[2]))
        fh.close()
        
        mergeVideoImage(file_dir)
        task_video.status = "PROCESADO"
        task_video.edited = file_dir
        session.commit()
        return video_schema.dump(task_video), 200

def mergeVideoImage(idrl_video):
    clip_1 = VideoFileClip(file_logo_dir)
    clip_2 = VideoFileClip(idrl_video)

    if(clip_2.duration > 18):
        clip_2 = clip_2.subclip(0,18)
        
    clip_3 = VideoFileClip(file_logo_dir)
    video = CompositeVideoClip([clip_1,
                                clip_2.set_start(1).set_position(("center","top")),
                                clip_3.set_start(clip_2.duration+1)], size=(1920,1080))
    video.write_videofile(idrl_video)