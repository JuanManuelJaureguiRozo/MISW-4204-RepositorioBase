from modelos import db, Video, VideoSchema
from sqlalchemy.orm import sessionmaker
from flask import Flask,request
from flask_restful import Api, Resource
import configparser
import base64
import json
import os

# gcloud
from google.cloud import storage

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

video_schema = VideoSchema()
Session = sessionmaker(bind=db)
session = Session()

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

class VideoComandsResource(Resource):
    def post(self):
        message = request.json['message']
        json_data = base64.b64decode(message['data']).decode('utf-8')
        data = json.loads(json_data)
        # print(data)
        id = data['id']
        video = session.query(Video).get(id)

        if video is None:
            return '', 404

        file_name = data['file_name']
        file = base64.b64decode(data['file'])
        upload_blob_from_memory(file, file_name)
        file_dir = "https://storage.cloud.google.com/almacenamiento_videos_e3/videos_originales/" + file_name

        video.status = "SUBIDO"
        video.original = file_dir
        session.commit()
        return video_schema.dump(video), 200
    
api = Api(app)
api.add_resource(VideoComandsResource, '/api/tasks')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
