from peewee import *
from playhouse.fields import PickleField


db = SqliteDatabase('db.sqlite3')


class BaseModel(Model):
	class Meta:
		database = db


class UserData(BaseModel):
	id = PrimaryKeyField()
	locale = CharField()
	allow_news = BooleanField()
	allow_messages = BooleanField()
	news_count = IntegerField()
	messages_count = IntegerField()
	session = PickleField(null=True)

	class Meta:
		table_name = 'user_data'
