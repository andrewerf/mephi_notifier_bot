

help_msg = '''
Login to system (username and password from auth.mephi.ru):
/login username password
Logout:
/logout
View status:
/status
Allow notifications:
/allow [messages | news | all]
Disallow notifications:
/disallow [messages | news | all]
Print this help:
/help
'''

welcome_msg = '''
Welcome to notifier-bot for home.mephi.ru messages and news
Quick guid:
	
''' + help_msg

status_msg = '''
Logged in: {}
Allowed: {} {}
'''

login_succeeds_msg = '''
Login succeeds
'''

logout_succeeds_msg = '''
Logout succeeds
'''

allow_succeeds_msg = '''
Notifications added
'''

disallow_succeeds_msg = '''
Notifications removed
'''