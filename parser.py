import requests
from bs4 import BeautifulSoup as bs


login_url = 'https://auth.mephi.ru/login'
home_url = 'https://home.mephi.ru/home'
headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
}


def login(username, password):
	s = requests.Session()
	s.headers = headers

	login_page = bs(s.get(login_url).content, 'lxml')
	token = login_page.find('input', {'name': 'authenticity_token'}).get('value')
	lt = login_page.find('input', {'name': 'lt'}).get('value')

	login_data = {
		'username': username,
		'password': password,
		'authenticity_token': token,
		'utf8': '✓',
		'lt': lt
	}
	s.post(login_url, login_data)

	return s


def get_msgs_count(session):
	home_page = bs(session.get(home_url, allow_redirects=True).content, 'lxml')
	ret = home_page.find('span', {'class': 'count_unread_talks'}, recursive=True).text
	return int(ret)


def get_news_count(session):
	home_page = bs(session.get(home_url, allow_redirects=True).content, 'lxml')
	ret = home_page.find('span', {'class': 'count_unread_news'}, recursive=True).text
	return int(ret)