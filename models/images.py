from models.base_model import BaseModel
from models.user import User
import peewee as pw
from playhouse.hybrid import hybrid_property


class Images(BaseModel):
    path = pw.CharField()
    user = pw.ForeignKeyField(User, backref='images')

    @hybrid_property
    def images_url(self):
        from helpers import S3_LOCATION
        return S3_LOCATION + self.path
