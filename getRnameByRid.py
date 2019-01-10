
# coding: utf-8

import requests
from bs4 import BeautifulSoup
def get_name(roomid):
	r = requests.get("http://www.douyu.com/" + roomid)
	soup = BeautifulSoup(r.text, 'lxml')
	print(soup.find_all('class'))
	#return soup.find('a', {'class', 'zb-name'}).string

if __name__ == '__main__':
	get_name('9999')