from datos import create_app
from flask_restful import Api
from flask_cors import CORS
from datos.api_commands import VideoComandsResource
from datos.api_queries import VideoQueriesResource
from datos.api_queries import VideoQueryResource
import os

app = create_app('default')
app_context = app.app_context()
app_context.push()

cors = CORS(app)

api = Api(app)
api.add_resource(VideoComandsResource, '/api/tasks', '/api/tasks/<int:id>')
api.add_resource(VideoQueriesResource, '/api/tasks')
api.add_resource(VideoQueryResource, '/api/tasks/<int:id>')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))