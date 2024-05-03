from celery import Celery
from modelos import db, Video, VideoSchema
from sqlalchemy.orm import sessionmaker
from flask import Flask,request
import configparser
import base64
# gcloud
from google.cloud import storage


config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

file_upload_dir = config['Paths']['file_upload_dir']
bucket_name = 'almacenamiento_videos_e3'
path_file = "videos_originales/"

# Crear la aplicación
def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgresql@localhost:5432/IDRL'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

app = create_app('default')
app_context = app.app_context()
app_context.push()

Session = sessionmaker(bind=db)
session = Session()

celery_app = Celery(__name__, broker='redis://localhost:6379/0')
@celery_app.task(name='upload_video')
def upload_video(*args):
    with app.app_context():
        video_schema = VideoSchema()
        # print(args)
        video = session.query(Video).get(args[0])

        if video is None:
            return '', 404

        file_name = args[1]
        file = base64.b64decode(args[2])
        upload_blob_from_memory(file, file_name)
        # write_on_bucket(file_name, file)
        file_dir = "gs://almacenamiento_videos_e3/videos_originales" + "/" + file_name
        # file_dir = file_upload_dir + "\\" + file_name
        # fh = open(file_dir, "wb")
        # fh.write(base64.b64decode(args[2]))
        # fh.close()

        video.status = "SUBIDO"
        video.original = file_dir
        session.commit()
        return video_schema.dump(video), 200
    
def write_on_bucket(blob_name,blob_object):
    """Write and read a blob from GCS using file-like IO"""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your new GCS object
    # blob_name = "storage-object-name"

    storage_client = storage.Client.from_service_account_json('service_account.json')

    bucket = storage_client.bucket(bucket_name)
    file = bucket.blob("videos_originales\\" + blob_name)
    file.upload_from_string(blob_object, content_type='video/mp4')
    file.make_public()
    # blob = bucket.blob(blob_name)

    # Mode can be specified as wb/rb for bytes mode.
    # See: https://docs.python.org/3/library/io.html
    #with blob.open("w") as f:
    #    f.write(blob_object)

def upload_blob_from_memory(contents, destination_blob_name):
    """Uploads a file to the bucket."""

    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The contents to upload to the file
    # contents = "these are my contents"

    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"
    destination_blob_name = path_file + destination_blob_name
    storage_client = storage.Client.from_service_account_json('C:/Users/PERSONAL/Documents/Proyectos_UniAndes/service_account.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents, content_type='video/mp4')

    print(
        f"{destination_blob_name} uploaded to {bucket_name}."
    )