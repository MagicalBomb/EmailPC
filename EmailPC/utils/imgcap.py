import sys
from PIL import ImageGrab
from PyQt5.QtWidgets import QApplication, qApp
from PyQt5.QtMultimedia import QCamera,QCameraInfo,QCameraImageCapture

from PyQt5.QtCore import pyqtSignal, QObject, QBasicTimer


class ImgCapture(QCameraImageCapture):
	"""
	
	"""

	#当拍照完成， 并且已经保存完图片发送本信号
	cameraCapOk = pyqtSignal(str)

	def __init__(self,parent = None):
		super(QCameraImageCapture, self).__init__(None,parent)

		self.camera = QCamera()
		self.camera.setCaptureMode(QCamera.CaptureStillImage);

		self.setMediaObject(self.camera)
		# self.setCaptureDestination(QCameraImageCapture.CaptureToFile)

		self.imageSaved.connect(self._captureComplete)
		self.imageCaptured.connect(self._imageCaptured)


	#图片保存的目录
	def cameraCapture(self,filename):
		self.camera.start()
		self.capture(filename)


	#屏幕截图，保存图片到指定目录下
	def screenCapture(self,filename):
		"""

		同 cameraCapture

		"""
		im = ImageGrab.grab()

		im.save(filename,'jpeg')


	def _imageCaptured(self,id,qImg):
		pass

	def _captureComplete(self,id,filename):
		self.camera.stop()
		self.cameraCapOk.emit(filename)
		# t = self.cancelCapture()
		# print(filename)
		# qApp.quit()
		# self.timer = QBasicTimer()
		# self.timer.start(3000,self)



if __name__ == '__main__':
	app = QApplication(sys.argv)

	o = ImgCapture()

	#摄像头拍照
	# o.CameraCapture(r"C:\Users\Magicalbomb\Desktop\Work\2.jpg")

	#屏幕截图
	# o.screenCapture(r"C:\Users\Magicalbomb\Desktop\Work\3.jpg")


	sys.exit(app.exec_())




