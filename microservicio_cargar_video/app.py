from modelos import db, Video
from sqlalchemy.orm import sessionmaker
from flask import Flask
import configparser
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
bucket_name = config['Paths']['bucket_name']
path_file = config['Paths']['path_file']
service_account = config['Paths']['service_account']

db_user = config['credentials']['db_user']
db_password = config['credentials']['db_password']
db_host = config['credentials']['db_host']
db_port = config['credentials']['db_port']
db_database = config['credentials']['db_database']

project_id = config['PUBSUB']['project_id']
topic_upload_id = config['PUBSUB']['topic_upload_id']
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

subscriber = pubsub_v1.SubscriberClient.from_service_account_json(service_account_sub)
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def upload_blob_from_memory(contents, destination_blob_name):
    """Uploads a file to the bucket."""
    destination_blob_name = path_file + destination_blob_name
    storage_client = storage.Client.from_service_account_json(service_account)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents, content_type='video/mp4')

    print(
        f"{destination_blob_name} uploaded to {bucket_name}."
    )

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    json_object = json.loads(message.data)
    print(f"Received {json_object.get('file_name')!r}.")
    video = session.query(Video).get(json_object.get('id'))

    if video is None:
        print(f"Error al subir video, el video no se encontró en la BD.")
        #return '', 404

    file_name = json_object.get('file_name')
    file = base64.b64decode(json_object.get('file'))
    upload_blob_from_memory(file, file_name)
    file_dir = "https://storage.cloud.google.com/almacenamiento_videos_e3/videos_originales/" + file_name

    video.status = "SUBIDO"
    video.original = file_dir
    session.commit()
    # return video_schema.dump(video), 200
    if message.attributes:
        print("Attributes:")
        for key in message.attributes:
            value = message.attributes.get(key)
            print(f"{key}: {value}")
    message.ack()


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")

# Wrap subscriber in a 'with' block to automatically call close() when done.
with subscriber:
    # When `timeout` is not set, result() will block indefinitely,
    # unless an exception is encountered first.
    try:
        streaming_pull_future.result(timeout=60)
    except Exception as e:
        print(
            f"Listening for messages on {subscription_path} threw an exception: {e}."
        )
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.
