from modelos import db, Video, VideoSchema
from sqlalchemy.orm import sessionmaker
from flask import Flask,request
from flask_restful import Api, Resource
import configparser
from moviepy.editor import VideoFileClip, CompositeVideoClip
import base64, json, tempfile
import os

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

video_schema = VideoSchema()
Session = sessionmaker(bind=db)
session = Session()

def mergeVideoImage(binary_data):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_file.write(binary_data)
    temp_file.close()

    try:
        clip_2 = VideoFileClip(temp_file.name)
    except:
        return None

    clip_1 = VideoFileClip(file_logo_dir)

    if(clip_2.duration > 18):
        clip_2 = clip_2.subclip(0,18)
        
    clip_3 = VideoFileClip(file_logo_dir)
    video = CompositeVideoClip([clip_1,
                                clip_2.set_start(1).set_position(("center","top")),
                                clip_3.set_start(clip_2.duration+1)], size=(1920,1080))
    
    temp_file_edited = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video.write_videofile(temp_file_edited.name)
    temp_file_edited.close()
    return temp_file_edited.name

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

class VideoComandsResource(Resource):
    def post(self):
        message = request.json['message']
        json_data = base64.b64decode(message['data']).decode('utf-8')
        data = json.loads(json_data)
        id = data['id']
        video = session.query(Video).get(id)

        if video is None:
            return '', 404

        file_name = data['file_name']
        file = base64.b64decode(data['file'])
        file_name = "edited_" + file_name
        file_dir = file_upload_dir + "/" + file_name

        temp_file_edited = mergeVideoImage(file)
        upload_blob_from_memory(temp_file_edited, file_name)
        file_dir = "https://storage.cloud.google.com/almacenamiento_videos_e3/videos_procesados/" + file_name
        video.status = "PROCESADO"
        video.edited = file_dir
        session.commit()
        return video_schema.dump(video), 200

api = Api(app)
api.add_resource(VideoComandsResource, '/api/tasks')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))