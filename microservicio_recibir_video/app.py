from microservicio_recibir_video import create_app, create_db
from .modelos import db
from flask_restful import Api
from flask_cors import CORS
from .api_commands import VideoComandsResource
from .api_queries import VideoQueriesResource
from .api_queries import VideoQueryResource

app = create_app('default')
app_context = app.app_context()
app_context.push()

cors = CORS(app)

api = Api(app)
api.add_resource(VideoComandsResource, '/api/tasks', '/api/tasks/<int:id>')
api.add_resource(VideoQueriesResource, '/api/tasks')
api.add_resource(VideoQueryResource, '/api/tasks/<int:id>')