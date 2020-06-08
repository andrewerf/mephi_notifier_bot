import logging
import i18n
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.update import Update

from sql_models import *
from sql_persistance import SqlPersistence
from parser import login, get_news_count, get_msgs_count


tr = i18n.t


def reply(update, context, msg):
	context.bot.send_message(update.effective_chat.id, msg)


def start_handler(update : Update, context : CallbackContext):
	context.user_data['id'] = update.effective_chat.id
	context.user_data['locale'] = 'en'
	context.user_data['session'] = 0
	context.user_data['allow_news'] = False
	context.user_data['allow_messages'] = False
	context.user_data['news_count'] = 0
	context.user_data['messages_count'] = 0

	reply(update, context, tr('messages.welcome', locale='en'))


def login_handler(update : Update, context : CallbackContext):
	if len(context.args) != 2:
		pass

	session = login(context.args[0], context.args[1])
	context.user_data['session'] = session
	
	reply(update, context, tr('messages.login_succeeds', locale=context.user_data['locale']))


def logout_handler(update : Update, context : CallbackContext):
	context.user_data['session'] = 0
	reply(update, context, tr('messages.logout_succeeds', locale=context.user_data['locale']))


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

	msg = tr('messages.status', locale=context.user_data['locale']).format(*tuple(ret))

	reply(update, context, msg)


def allow_handler(update : Update, context : CallbackContext):
	if len(context.args) != 1:
		pass

	cmd = context.args[0]
	if cmd == 'news' or cmd == 'all':
		context.user_data['allow_news'] = True
	if cmd == 'messages' or cmd == 'all':
		context.user_data['allow_messages'] = True

	reply(update, context, tr('messages.allow_succeeds', locale=context.user_data['locale']))


def disallow_handler(update : Update, context : CallbackContext):
	if len(context.args) != 1:
		pass

	cmd = context.args[0]
	if cmd == 'news' or cmd == 'all':
		context.user_data['allow_news'] = False
	if cmd == 'messages' or cmd == 'all':
		context.user_data['allow_messages'] = False

	reply(update, context, tr('messages.disallow_succeeds', locale=context.user_data['locale']))


def help_handler(update : Update, context : CallbackContext):
	reply(update, context, tr('messages.help', locale=context.user_data['locale']))


def locale_handler(update : Update, context : CallbackContext):
	new_loc = context.args[0]
	if new_loc not in ['en', 'ru']:
		reply(update, context, tr('messages.incorrect_locale', locale=context.user_data['locale']))
	else:
		context.user_data['locale'] = new_loc
		reply(update, context, tr('messages.locale_changed', locale=new_loc).format(new_loc))


def notify(context : CallbackContext):
	for data in context.dispatcher.user_data.values():
		if data['session'] == 0:
			continue

		msg = ''
		news_count = get_news_count(data['session'])
		messages_count = get_msgs_count(data['session'])

		if news_count > data['news_count'] and data['allow_news']:
			msg += tr('messages.new_update', locale=context.user_data['locale'])
		if messages_count > data['messages_count'] and data['allow_messages']:
			msg += tr('messages.new_message', locale=context.user_data['locale'])

		if len(msg) > 0:
			context.bot.send_message(data['id'], msg)

		data['news_count'] = news_count
		data['messages_count'] = messages_count


if __name__ == '__main__':
	i18n.load_path.append('text')
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
	dp.add_handler(CommandHandler('locale', locale_handler))

	job_queue.run_repeating(notify, interval=5, first=10)

	updater.start_polling()


