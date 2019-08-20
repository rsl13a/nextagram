from models.base_model import BaseModel
import peewee as pw
from playhouse.hybrid import hybrid_property


class User(BaseModel):
    username = pw.CharField(unique=True)
    password = pw.CharField()
    email = pw.CharField(unique=True)
    # filename = pw.CharField()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    # @hybrid_property
    # def full_picture_url(self):
    #     return f"{os.getenv('S3_LOCATION')}/{self.filename}"
