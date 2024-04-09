from microservicio_recibir_video import create_app, create_db
from .modelos import db
from flask_restful import Api
from flask_cors import CORS
from .api_commands import VideoComandsResource
from .api_queries import VideoQueriesResource

app = create_app('default')
app_context = app.app_context()
app_context.push()

cors = CORS(app)

api = Api(app)
api.add_resource(VideoComandsResource, '/videos', '/videos/<int:id>')
api.add_resource(VideoQueriesResource, '/videos')