from flask_restful import Resource
from .modelos import db, Video, VideoSchema
from flask import request
# from flask_jwt_extended import jwt_required, create_access_token
from celery import Celery
from datetime import datetime

celery_app = Celery(__name__, broker='redis://localhost:6379/0')

@celery_app.task(name='upload_video')
def upload_video(*args):
    pass

video_schema = VideoSchema()

class VideoComandsResource(Resource):
    def post(self):
        print(request)
        print('prueba')
        file_name = request.form['file_name']
        timestamp = request.form['timestap']
        status = request.form['status']
        original = None
        edited = None
        video = Video(file_name=file_name, timestamp=timestamp, status=status, original=original, edited=edited)
        args = (file_name, timestamp, status, original, edited)
        upload_video.apply_async(args=args, queue='logs')
        db.session.add(video)
        db.session.commit()
        return video_schema.dump(video), 201
    
    def put(self, id):
        video = Video.query.get_or_404(id)
        video.status = request.json['status']
        db.session.commit()
        return video_schema.dump(video), 200

    def delete(self, id):
        video = Video.query.get_or_404(id)
        db.session.delete(video)
        db.session.commit()
        return '', 204