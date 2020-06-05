from collections import defaultdict
from telegram.ext import BasePersistence
from peewee import Database
from playhouse.shortcuts import model_to_dict


class SqlPersistence(BasePersistence):
	def __init__(self, database : Database,
				 store_user_data=True,
				 store_chat_data=True,
				 store_bot_data=True,
				 user_data_model=None,
				 chat_data_model=None,
				 bot_data_model=None):
		super().__init__(store_user_data, store_chat_data, store_bot_data)

		self.database = database
		self.user_data = None
		self.chat_data = None
		self.bot_data = None
		self.user_data_model = user_data_model
		self.chat_data_model = chat_data_model
		self.bot_data_model = bot_data_model

		self.database.connect(True)
		to_create = []
		if self.user_data_model is not None:
			to_create.append(self.user_data_model)
		if self.chat_data_model is not None:
			to_create.append(self.chat_data_model)
		if self.bot_data_model is not None:
			to_create.append(self.bot_data_model)

		self.database.create_tables(to_create, safe=True)

	def flush(self):
		self.database.close()

	def get_user_data(self):
		ret = defaultdict(dict)
		query = self.user_data_model.select()
		for user in query:
			ret[user.id] = model_to_dict(user)
		return ret

	def get_chat_data(self):
		ret = defaultdict(dict)
		query = self.chat_data_model.select()
		for chat in query:
			ret[chat.id] = model_to_dict(chat)
		return ret

	def get_bot_data(self):
		ret = self.bot_data_model.select()
		return model_to_dict(ret)

	def update_user_data(self, user_id, data):
		data['id'] = user_id
		self.user_data_model.replace(**data).execute()

	def update_chat_data(self, chat_id, data):
		data['id'] = chat_id
		self.chat_data_model.replace(**data).execute()

	def update_bot_data(self, data):
		self.bot_data_model.replace(**data).execute()

	# not implemented yet
	def get_conversations(self, name):
		pass

	# not implemented yet
	def update_conversation(self, name, key, new_state):
		pass