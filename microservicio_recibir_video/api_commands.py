from flask_restful import Resource
from .modelos import db, Video, VideoSchema
from flask import request
# from flask_jwt_extended import jwt_required, create_access_token
from celery import Celery
from sqlalchemy.orm import sessionmaker

celery_app = Celery(__name__, broker='redis://localhost:6379/0')

@celery_app.task(name='upload_video')
def upload_video(*args):
    pass

video_schema = VideoSchema()
Session = sessionmaker(bind=db)
session = Session()

class VideoComandsResource(Resource):
    def post(self):
        vfile_name = request.json['file_name']
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
        args = (vfile_name, vtimestamp, vstatus, voriginal, vedited)
        upload_video.apply_async(args=args, queue='logs')
        return video_schema.dump(nuevo_video), 201
    
    def put(self, id):
        video = session.query(Video).get_or_404(id)
        video.status = request.json['status']
        video.original = request.json['original']
        video.edited = request.json['edited']
        session.commit()
        return video_schema.dump(video), 200

    def delete(self, id):
        video = session.query(Video).get_or_404(id)
        session.delete(video)
        session.commit()
        return '', 204