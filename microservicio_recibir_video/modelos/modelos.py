from sqlalchemy import create_engine, Column, Integer, String, Enum, Table, MetaData
from microservicio_recibir_video import create_db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from sqlalchemy.ext.declarative import declarative_base
import enum

db = create_db()
Base = declarative_base()

try:
    with db.connect() as connection_str:
        print('Successfully connected to the PostgreSQL database')
except Exception as ex:
    print(f'Sorry failed to connect: {ex}')

class Estado(enum.Enum):
    PENDIENTE = 0
    CREADO = 1
    SUBIDO = 2
    PROCESADO = 3

class Video(Base):
    __tablename__ = 'video'
    id = Column(Integer, primary_key=True)
    file_name = Column(String(128), nullable=False)
    timestamp = Column(String(50), nullable=False)
    status = Column(Enum(Estado), nullable=False)
    original = Column(String(128))
    edited = Column(String(128))

    def __init__(self, file_name, timestamp, status, original, edited):
        self.file_name = file_name
        self.timestamp = timestamp
        self.status = status
        self.original = original
        self.edited = edited

    def __repr__(self):
        return f'<Video {self.id}>'

class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {"llave": value.name, "valor": value.value}
    
class VideoSchema(SQLAlchemyAutoSchema):
    status = EnumADiccionario(attribute=("status"))
    class Meta:
         model = Video
         include_relationships = True
         load_instance = True