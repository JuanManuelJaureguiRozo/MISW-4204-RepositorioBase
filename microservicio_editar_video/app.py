from celery import Celery
from modelos import db, Video, VideoSchema
from sqlalchemy.orm import sessionmaker
from flask import Flask,request
import configparser
import cv2 as cv2
from moviepy.editor import VideoFileClip, concatenate_videoclips,CompositeVideoClip
import base64
# gcloud
from google.cloud import storage

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

file_upload_dir = config['Paths']['file_upload_dir']
file_logo_dir = config['Paths']['file_logo_dir']
bucket_name = config['Paths']['bucket_name']
path_file = config['Paths']['path_file']
service_account = config['Paths']['service_account']
db_user = config['credentials']['db_user']
db_password = config['credentials']['db_password']
db_host = config['credentials']['db_host']
db_port = config['credentials']['db_port']
db_database = config['credentials']['db_database']

# Crear la aplicación
def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://'+ db_user +':'+ db_password +'@'+ db_host +':'+ db_port +'/' + db_database
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
        file_name = "edited_" + file_name
        file_dir = file_upload_dir + "\\" + file_name
        fh = open(file_dir, "wb")
        fh.write(base64.b64decode(args[2]))
        fh.close()

        mergeVideoImage(file_dir)
        upload_blob_from_memory(file_dir, file_name)
        file_dir = "https://storage.cloud.google.com/almacenamiento_videos_e3/videos_procesados/" + file_name
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

def upload_blob_from_memory(contents, destination_blob_name):
    """Uploads a file to the bucket."""
    destination_blob_name = path_file + destination_blob_name
    storage_client = storage.Client.from_service_account_json(service_account)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(contents, content_type='video/mp4')

    print(
        f"{destination_blob_name} uploaded to {bucket_name}."
    )