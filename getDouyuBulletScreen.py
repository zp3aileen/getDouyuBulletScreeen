# coding: utf-8

import multiprocessing
import socket
import time
import re
import pymongo
import requests
from bs4 import BeautifulSoup

clients = pymongo.MongoClient('localhost')
db = clients["DouyuTV_BulletScreen"]
col = db["info"]

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname("openbarrage.douyutv.com")
port = 8601
client.connect((host, port))

bullet_screen_path = re.compile(b'txt@=(.+?)/cid@')
uid_path = re.compile(b'uid@=(.+?)/nn@')
nickname_path = re.compile(b'nn@=(.+?)/txt@')
level_path = re.compile(b'level@=([1-9][0-9]?)/sahf')

def sendMsg(msgstr):
	msg = msgstr.encode('utf-8')
	data_length = len(msg) + 8
	code = 689
	msgHead = int.to_bytes(data_length, 4, 'little') + int.to_bytes(data_length, 4, 'little') + int.to_bytes(data_length, 4, 'little')
	client.send(msgHead)
	sent = 0
	while sent < len(msg):
		tn = client.send(msg[sent:])
		sent = sent + tn

def start(roomid):
	msg = 'type@=loginreq/username@=paul001000/password@=secret/roomid@={}/\0'.format(roomid)
	sendMsg(msg)
	msg_more = 'type@=joingroup/rid@={}/gid@=-9999/\0'.format(roomid)
	sendMsg(msg_more)

	print('-------welcome to {} `s room-------'.format(get_name(roomid)))
	while True:
		data = client.recv(1024)
		uid_more = uid_path.findall(data)
		nickname_more = nickname_path.findall(data)
		level_more = level_path.findall(data)
		bullet_screen_more = bullet_screen_path.findall(data)
		if not level_more:
			level_more = b'0'
		if not data:
			break
		else:
			for i in range(0, len(bullet_screen_more)):
				try:
					product = {
						'uid': uid_more[0].decode(encoding='utf-8'),
						'nickname': nickname_more[0].decode(encoding='utf-8'),
						'level': level_more[0].decode(encoding='utf-8'),
						'bullet_screen': bullet_screen_more[0].decode(encoding='utf-8')
					}
					print(product)
					col.insert(product)
					print('import to mongdb success')
				except Exception as e:
					print(e)

def keeplive():
	while True:
		msg = 'type@=keeplive/tick@=' + str(int(time.time())) + '/\0'
		sendMsg(msg)
		time.sleep(15)

def get_name(roomid):
	r = requests.get("http://www.douyu.com/" + roomid)
	soup = BeautifulSoup(r.text, 'lxml')
	return soup.find('a', {'class', 'zb-name'}).string


if __name__ == '__main__':
	roomid = '9999'
	p1 = multiprocessing.Process(target=start, args=(roomid,))
	p2 = multiprocessing.Process(target=keeplive)
	p1.start()
	p2.start()