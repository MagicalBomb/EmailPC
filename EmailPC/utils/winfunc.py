import shutil
import os
import tempfile
from ctypes import *



def getStartUpFolderPath():
	"""
	这个函数当前目录下必须有
	StartUpFolderPath.dll
	这个dll

	返回：

		自启动目录的地址 ： str
	"""
	#StartUpFolderPath
	curdir = os.path.dirname(__file__)
	dllpath = os.path.join(curdir,"StartUpFolderPath.dll")
	my_dll = cdll.LoadLibrary(dllpath)
	p_buf = create_unicode_buffer(1024)
	my_dll.StartUpFolderPath(p_buf)
	# return p_buf.value
	
	return p_buf.value



def copyFile(src,dst):
	"""
		shutil 提供的 copy 函数不但复制文件的内容， 同时
		也复制源文件的读写权限等， 但是像 创建时间戳 这样的元
		数据是无法复制的

		dst 可以是一个目录的名字， 这样就会使用 src 中的文件名字了

		注意：

			会覆盖源文件
	"""
	shutil.copy(src,dst)


#输入 Windows 的 CMD 命令， 返回执行结果
def cmd(command):
	res = os.system(command)
	return res

#返回指定目录下的所有文件和目录， 不包括当前和上级目录(.和..)
def listDir(dir):
	return os.listdir(dir)

if __name__ == '__main__':
	# s = GetStartUpFolderPath()
	# print(s)
	# curdir = os.path.dirname(__file__)
	# print(os.path.join(curdir,))
	copyFile(r"C:\Users\Magicalbomb\Desktop\Work\2.jpg",r"C:\Users\Magicalbomb\Desktop")
	pass