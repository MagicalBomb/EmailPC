import sys
import os
from PyQt5.QtCore import QObject, QBasicTimer
from PyQt5.QtWidgets import QApplication, qApp
from utils import emailhelper
import time

class MyCls:

	def __init__(self):
		print("我的ID是: {}".format(id(self)))


if __name__ == '__main__':
	smtpserv = "smtp.163.com"
	smtpport = 25
	user = "17826800084@163.com"
	pwd = "shagua.116wy"
	title = "嗨，你好啊"
	msg = "我什么事情也没有"

	print("5s 之后发送")

	time.sleep(5)

	# emailhelper.send(smtpserv,smtpport,user,pwd,user,title,msg)
	emailhelper.recv(smtpserv,smtpport,user,pwd)