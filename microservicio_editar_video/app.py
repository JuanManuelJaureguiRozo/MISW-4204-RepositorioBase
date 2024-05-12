from modelos import db, Video, VideoSchema
from sqlalchemy.orm import sessionmaker
from flask import Flask,request
import configparser
import cv2 as cv2
from moviepy.editor import VideoFileClip, CompositeVideoClip
import base64
import json

# gcloud
from google.cloud import storage
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError

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

project_id = config['PUBSUB']['project_id']
topic_edit_id = config['PUBSUB']['topic_edit_id']
service_account_sub = config['PUBSUB']['service_account_sub']
subscription_id = config['PUBSUB']['subscription_id']

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


subscriber = pubsub_v1.SubscriberClient.from_service_account_json(service_account_sub)
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# Limit the subscriber to only have ten outstanding messages at a time.
flow_control = pubsub_v1.types.FlowControl(max_messages=1)

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    json_object = json.loads(message.data)
    print(f"Received {json_object.get('file_name')!r}.")
    video_schema = VideoSchema()
    task_video = session.query(Video).get(json_object.get('id'))

    if task_video is None:
        return '', 404

    file_name = json_object.get('file_name')
    file = base64.b64decode(json_object.get('file'))
    file_name = "edited_" + file_name
    file_dir = file_upload_dir + "/" + file_name
    fh = open(file_dir, "wb")
    fh.write(file)
    fh.close()

    mergeVideoImage(file_dir)
    upload_blob_from_memory(file_dir, file_name)
    file_dir = "https://storage.cloud.google.com/almacenamiento_videos_e3/videos_procesados/" + file_name
    task_video.status = "PROCESADO"
    task_video.edited = file_dir
    session.commit()
    message.ack()
    # return video_schema.dump(task_video), 200
    


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback,flow_control=flow_control)
print(f"Listening for messages on {subscription_path}..\n")

# Wrap subscriber in a 'with' block to automatically call close() when done.
with subscriber:
    # When `timeout` is not set, result() will block indefinitely,
    # unless an exception is encountered first.
    try:
        streaming_pull_future.result()
    except Exception as e:
        print(
            f"Listening for messages on {subscription_path} threw an exception: {e}."
        )
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.