from flask_restful import Resource
from modelos import db, Video, VideoSchema
from flask import request
# from flask_jwt_extended import jwt_required, create_access_token
from celery import Celery
from sqlalchemy.orm import sessionmaker
from google.cloud import pubsub_v1
import configparser
import json

config = configparser.ConfigParser()
config.sections()
config.read('config.ini')

project_id = config['PUBSUB']['project_id']
topic_upload_id = config['PUBSUB']['topic_upload_id']
topic_edit_id = config['PUBSUB']['topic_edit_id']
service_account = config['Paths']['service_account']

video_schema = VideoSchema()
Session = sessionmaker(bind=db)
session = Session()

class VideoComandsResource(Resource):
    def post(self):
        vfile_name = request.json['file_name']
        vfile = request.json['file']
        vtimestamp = request.json['timestap']
        vstatus = request.json['status']
        voriginal = None
        vedited = None
        
        nuevo_video = Video(
            file_name = vfile_name,
            timestamp = vtimestamp,
            status = vstatus,
            original = voriginal,
            edited = vedited
        )
    
        session.add(nuevo_video)
        session.commit()

        video = {}
        video['id'] = nuevo_video.id
        video['file_name'] = nuevo_video.file_name
        video['file'] = vfile

        publish_messages(topic_upload_id,json.dumps(video))
        publish_messages(topic_edit_id,json.dumps(video))
        return video_schema.dump(nuevo_video), 201
    
    
    def put(self, id):
        video = session.query(Video).get(id)

        if video is None:
            return '', 404

        video.status = request.json['status']
        video.original = request.json['original']
        video.edited = request.json['edited']
        session.commit()
        return video_schema.dump(video), 200

    def delete(self, id):
        video = session.query(Video).get(id)

        if video is None:
            return '', 404

        session.delete(video)
        session.commit()
        return '', 204
    
    
def publish_messages(topic_id: str,message) -> None:
    publisher = pubsub_v1.PublisherClient.from_service_account_json(service_account)
    topic_path = publisher.topic_path(project_id, topic_id)
    future = publisher.publish(topic_path, message.encode('utf-8') )
    print(future.result())
    print(f"Published messages to {topic_path}.")