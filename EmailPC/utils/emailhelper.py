import smtplib,poplib,os
from socket import gaierror
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.parser import BytesParser
from email.header import decode_header


__all__ = ['recv','send']


DEBUG = False

def debug_log(msg):
    if DEBUG:
        print(msg)


def recv(popserver, popport, user, pwd):
    """
    参数：

        基本跟 send 函数一样

    返回：

        二元组 （title ， msg_content）
        都已经是 str 了


    注意：

        1. 如果发送的时候， 未连接网络， 会抛出 socket.gaierror 异常

    """

    from pprint import pprint as pp
	#登陆 POP 
    pop = poplib.POP3(popserver,popport)
    pop.set_debuglevel(0)
    pop.user(user)
    pop.pass_(pwd)


    # response = pop.list()
    # pp(response)


    #获得最新一封的邮件
    #--邮箱状态 （邮件数量， 邮箱大小）
    msg_count , mailbox_size = pop.stat()
    #--lines ： list(bytes)
    response,lines,octs = pop.retr(msg_count)
    msg = b"\r\n".join(lines)
    # pp(lines)

    #将获得的消息， 转换成 Message 对象
    msg_parser = BytesParser()
    # msg_obj : email.message.Message
    msg_obj = msg_parser.parsebytes(msg)

    #获得 标题
    #decoe_header -> [(title:bytes,charset:str)]
    #如果标题，没有使用编码， 就是ascii，就不会有 charset ， （被设置为 None）
    r = decode_header(msg_obj['Subject'])
    debug_log(msg_obj['Subject'])
    debug_log(r)
    title = r[0][0]
    charset = r[0][1]
    if charset:
        title = title.decode(charset)

    #获得消息内容
    body = ""
    for part in msg_obj.walk():
        if(part.get_content_type() == "text/plain"):
            charset = part.get_content_charset()
            body = part.get_payload(decode=True)
            if charset:
                body = body.decode(charset)

    debug_log("emailhelper 接受消息成功。 title : {}".format(title))

    return title,body


def send(smtpserver, smtpport, user, passwd, mailto, title, msg=None, imgList = None):
    """
    参数： 
        
        msg 字符串类型， 消息的内容
        img 是二进制图片数据列表， 不是文件名， 可以一次发送多个图片

    注意：
        
        1. 使用 163 邮箱， 如果标题和内容不够好， 会被认为是垃圾邮件， 触发 STMPDataError 异常， 里面是 554 代码

        2. 如果发送的时候， 未连接网络， 会抛出 socket.gaierror 异常

    """
    #创建 EMAIL 消息
    email_msg = MIMEMultipart('mixed')
    email_msg['Subject'] = title
    email_msg['From'] = user
    #-  文本消息
    if(msg):
        email_msg_text = MIMEText(msg,_charset="utf8")
        email_msg.attach(email_msg_text)

    #-  图片消息
    if(imgList):
        for img in imgList:
            email_msg_img = MIMEImage(img)
            email_msg.attach(email_msg_img)

    #登陆SMTP
    smtp = smtplib.SMTP(smtpserver,smtpport)
    smtp.set_debuglevel(0)
    smtp.login(user,passwd)

    #发送消息
    smtp.sendmail(user,user,email_msg.as_string())
    #smtp.quit()

    debug_log("emailhelper 发送消息成功。 title : {}".format(title))


#这个类代表封邮件， 可以包含图片和文字
class EmailMessage:

    def __init__(self):
        
        self.reset()

    #设置标题
    def setTitle(self,title):
        self._Title = title

    #imgData 必须是图片数据
    def addImg(self,imgData):
        self._Imgs.append(imgData)

    #加入一段文字
    def addText(self,text):
        self._Text.append(text)

    def setFinished(self,f):
        self._IsFinished = f

    def IsFinished(self):
        return self._IsFinished

    #清空所有属性
    def reset(self):
        self._Text = []
        self._Imgs = []
        self._Title = ""
        #用来表示这封邮件是否完成
        self._IsFinished = True

    #发送消息， 并且重置当前的状态
    #如果是未完成的状态， 这个函数不会有任何的反应
    def sendAndReset(self,smtpserv,smtpport,user,pwd,mailto):
        if not self._IsFinished: return

        msg = ""
        for e in self._Text:
            msg += e
            msg += "\n"

        try:
            send(smtpserv,smtpport,user,pwd,mailto, self._Title,msg,self._Imgs)
        except gaierror:
            debug_log("sendAndReset : 无法发送消息，请检查网络")

        self.reset()

def _testSend():
    smtpserver = r"smtp.163.com"
    smtpport = 25
    user = "17826800084@163.com"
    pwd = "shagua.116wy"
    mailto = user
    title = "你好"
    msg = "你猜猜我是谁"
    img_path = r"C:\Users\Magicalbomb\Desktop\Work\1.png"
    send(smtpserver,smtpport,user,pwd,mailto,title,msg)
    # with open(img_path,'rb') as img:
    #     send(smtpserver,smtpport,user,pwd,mailto,title,msg,img.read())


if __name__ == '__main__':
    popserver = "pop.163.com"
    popport = 110
    user = "17826800084@163.com"
    pwd = "shagua.116wy"
    title, body = recv(popserver,popport,user,pwd)
    print(title, body)

