from .modelos import db, Video, VideoSchema
from flask_restful import Resource
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

video_schema = VideoSchema()
Session = sessionmaker(bind=db)
session = Session()

class VideoQueriesResource(Resource):
    def get(self):
        videos = session.query(Video).all()
        return video_schema.dump(videos, many=True), 200