from flask_restful import Resource
from modelos import db, Video, VideoSchema
from flask import request
# from flask_jwt_extended import jwt_required, create_access_token
from celery import Celery
from sqlalchemy.orm import sessionmaker

celery_app = Celery(__name__, broker='redis://127.0.0.1:6379/0')

@celery_app.task(name='upload_video')
def upload_video(*args):
    pass

@celery_app.task(name='edit_video')
def edit_video(*args):
    pass

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
        args = (nuevo_video.id,nuevo_video.file_name,vfile,nuevo_video.timestamp, vstatus, nuevo_video.original, nuevo_video.edited)
        upload_video.apply_async(args=args, queue='upload')
        edit_video.apply_async(args=args, queue='edit')
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