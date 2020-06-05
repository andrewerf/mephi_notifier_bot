import logging
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.update import Update

from sql_models import *
from sql_persistance import SqlPersistence
from parser import login, get_news_count, get_msgs_count
from bot_messages import *


def reply(update, context, msg):
	context.bot.send_message(update.effective_chat.id, msg)


def start_handler(update : Update, context : CallbackContext):
	context.user_data['id'] = update.effective_chat.id
	context.user_data['session'] = 0
	context.user_data['allow_news'] = False
	context.user_data['allow_messages'] = False
	context.user_data['news_count'] = 0
	context.user_data['messages_count'] = 0

	reply(update, context, welcome_msg)


def login_handler(update : Update, context : CallbackContext):
	if len(context.args) != 2:
		pass

	session = login(context.args[0], context.args[1])
	context.user_data['session'] = session
	
	reply(update, context, login_succeeds_msg)


def logout_handler(update : Update, context : CallbackContext):
	context.user_data['session'] = 0
	reply(update, context, logout_succeeds_msg)


def status_handler(update : Update, context : CallbackContext):
	nothing = True
	ret = []

	if context.user_data['session'] == 0:
		ret.append('no')
	else:
		ret.append('yes')

	if context.user_data['allow_news']:
		ret.append('news')
		nothing = False
	else:
		ret.append('')
	if context.user_data['allow_messages']:
		ret.append('messages')
		nothing = False
	else:
		ret.append('')

	if nothing:
		ret[1] = 'nothing'

	msg = status_msg.format(*tuple(ret))

	reply(update, context, msg)


def allow_handler(update : Update, context : CallbackContext):
	if len(context.args) != 1:
		pass

	cmd = context.args[0]
	if cmd == 'news' or cmd == 'all':
		context.user_data['allow_news'] = True
	if cmd == 'messages' or cmd == 'all':
		context.user_data['allow_messages'] = True

	reply(update, context, allow_succeeds_msg)


def disallow_handler(update : Update, context : CallbackContext):
	if len(context.args) != 1:
		pass

	cmd = context.args[0]
	if cmd == 'news' or cmd == 'all':
		context.user_data['allow_news'] = False
	if cmd == 'messages' or cmd == 'all':
		context.user_data['allow_messages'] = False

	reply(update, context, disallow_succeeds_msg)


def help_handler(update : Update, context : CallbackContext):
	reply(update, context, help_msg)


def notify(context : CallbackContext):
	for data in context.dispatcher.user_data.values():
		if data['session'] == 0:
			continue

		msg = ''
		news_count = get_news_count(data['session'])
		messages_count = get_msgs_count(data['session'])

		if news_count > data['news_count'] and data['allow_news']:
			msg += 'New update on home.mephi.ru!\n'
		if messages_count > data['messages_count'] and data['allow_messages']:
			msg += 'New message on home.mephi.ru!'

		if len(msg) > 0:
			context.bot.send_message(data['id'], msg)

		data['news_count'] = news_count
		data['messages_count'] = messages_count


if __name__ == '__main__':
	logging.basicConfig(filename='/var/log/mephi_notifier_bot.log', level=logging.WARNING)
	storage = SqlPersistence(db, True, False, False, UserData)
	updater = Updater(token="1099627440:AAFyWjowulFH_f_a4Y_mnDiO7pYngvFcQhM", use_context=True, persistence=storage)

	job_queue = updater.job_queue
	dp = updater.dispatcher

	dp.add_handler(CommandHandler('start', start_handler))
	dp.add_handler(CommandHandler('status', status_handler))
	dp.add_handler(CommandHandler('allow', allow_handler))
	dp.add_handler(CommandHandler('disallow', disallow_handler))
	dp.add_handler(CommandHandler('login', login_handler))
	dp.add_handler(CommandHandler('logout', logout_handler))
	dp.add_handler(CommandHandler('help', help_handler))

	job_queue.run_repeating(notify, interval=5, first=10)

	updater.start_polling()


