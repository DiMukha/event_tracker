import os
import uuid
import functools

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow.exceptions import ValidationError
# from flasgger import Swagger


class DevConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


configs = {
    'dev': DevConfig
}

app = Flask(__name__)
app.config.from_object(configs[os.getenv("FLASK_ENV")])
db = SQLAlchemy(app)
api = Api(app)
# swagger = Swagger(app)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    descr = db.Column(db.String(2000))
    dt = db.Column(db.DateTime)
    address = db.Column(db.String(200))
    ext_id = db.Column(db.String(36))
    priv_id = db.Column(db.String(36))

    def __init__(self, title, descr, dt, address):
        self.title = title
        self.descr = descr
        self.dt = dt
        self.address = address
        self.ext_id = str(uuid.uuid4())
        self.priv_id = str(uuid.uuid4())

    def __repr__(self):
        return f"Event(self.title, self.dt)"


class EventSchemaPost(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        exclude = "ext_id", "priv_id", "id"
        load_instance = True


class EventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        exclude = "id",


class EventSchemaGet(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        exclude = "id", "priv_id"


event_schema_post = EventSchemaPost()
event_schema = EventSchema()
event_schema_get = EventSchemaGet()


class EventListApi(Resource):
    def get(self):
        """
        Get all events
        ---
        responses:
            200:
                description: A list of events
        """
        events = db.session.query(Event).all()
        return events

    def post(self):
        """
        Create new event
        ---
        requestBody:
            content:
                application/json:
                    type: object
        responses:
            201:
                description: Create
            400:
                description: Validation error
        """
        try:
            event = event_schema_post.load(request.json, session=db.session)
        except ValidationError as e:
            return str(e), 400
        db.session.add(event)
        db.session.commit()
        return event_schema.dump(event), 201


def get_event(f):
    @functools.wraps(f)
    def wrapper(self, ext_id):
        event = db.session.query(Event).filter_by(ext_id=ext_id).first()
        if not event:
            return '{"message": "event not found"}', 404
        return f(self, event)
    return wrapper


class EventApi(Resource):
    @get_event
    def get(self, event):
        return event_schema_get.dump(event)

    @get_event
    def delete(self, event):
        db.session.delete(event)
        db.session.commit()
        return "", 204

    @get_event
    def put(self, event):




api.add_resource(EventListApi, '/events')
api.add_resource(EventApi, '/events/<ext_id>')

if __name__ == '__main__':
    app.run(debug=True)
