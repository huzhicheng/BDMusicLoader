#-*- coding:utf-8 -*-
'''
Created on 2014��3��6��

@author: huzhicheng
'''
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys,time,os
import threading
import urllib,urllib2,cookielib,re,codecs
from HTMLParser import HTMLParser
import re
from threading import Thread, RLock
from Queue import Queue
from helper import helper
reload(sys) 
sys.setdefaultencoding('utf-8')


#TODO:htmlparser
class MyClass(HTMLParser):
    processing = None
    singerProcessing = None
    links = []
    singers=[]
    songs = []
    tempHref=''
    title = ""
    href=""
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        HTMLParser.__init__(self) 
        
        
    def handle_starttag(self,tag,attrs):
        self.processing = None
        self.singerProcessing = None
        reg= re.compile(r"/song/[\d]{9}") #正则匹配
        #regSinger = re.compile(r"/artist/\d+")
        if tag=="a":
            for name,value in attrs:
                if name=="href" and reg.match(value):
                    self.href="http://music.baidu.com"+value
                    self.tempHref = value  #/song/198877373
                    self.processing = tag
#                 if name=="href" and regSinger.match(value):
#                     self.singerProcessing = True
        if tag=="span": #匹配歌手
            for name,value in attrs:
                if name=="title" and ('class', 'author_list') in attrs:
                    self.singers.append(value)
    
                
    
    def handle_data(self,data): 
        '''
        处理innerText内容  此处就是歌曲的标题
        '''
        if self.processing: 
            self.links.append([data,self.href,self.tempHref])   #self.links.appen("歌曲标题","http://music.baidu.com/song/198877373","/song/121212")      
            self.songs.append(data)
            #print data
        if self.singerProcessing:
            self.singers.append(data)
            

class DownloadHTMLParser(HTMLParser):
    '''
    
    '''
    mp3_128kbpsFiles=[]
    curTag = None
    
    def init(self):
        super.__init__(DownloadHTMLParser,self)
        
    def handle_starttag(self,tag,attrs):  
        self.curTag=None 
        i = 1
        if tag=="a":
            for name,value in attrs:
                if name=="href" and ('id','128') in attrs:
                    link = "http://music.baidu.com%s" % (value)
                    if link not in self.mp3_128kbpsFiles:
                        self.mp3_128kbpsFiles.append("http://music.baidu.com%s" % (value))
                        i+=1


class linkboard(QtGui.QDialog):
    
    def __init__(self,args,parent=None):
        super(linkboard,self).__init__(parent)
        text = QtGui.QTextEdit()
        text.setText(args)
        self.mainLayout = QtGui.QHBoxLayout()
        self.mainLayout.addWidget(text)
        self.setLayout(self.mainLayout)  
        
class fzDownloadButton(QtGui.QPushButton):
    '''
    classdocs
    '''


    def __init__(self,rowNum,columnNum,parent=None):
        super(fzDownloadButton,self).__init__(parent) 
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet('''QPushButton{background-image:url(./img/downloads.png);width:27px;height:28px;padding:0px;border:0px;}''')
        self.clicked.connect(self.emitClickWithParam)
        self.row = rowNum
        self.column = columnNum
        
    def emitClickWithParam(self):
        self.emit(QtCore.SIGNAL("downloadclick(int,int)"),self.row ,self.column)
        
class helper(object):
    '''
    classdocs
    '''
    rowCount = 0
    songAddresses=[]
    currentPath = os.getcwd()+"\config"


    def __init__(self, params):
        
        '''
        Constructor
        '''
    
    
    
    def BuildPostData(self,token,userInfo):
        jumppage = "http://www.baidu.com/cache/user/html/jump.html"

        postDict = {
            'charset':"utf-8",
            'token':token, #de3dbf1e8596642fa2ddf2921cd6257f
            'isPhone':"false",
            'index':"0",
            'staticpage':jumppage, #http%3A%2F%2Fwww.baidu.com%2Fcache%2Fuser%2Fhtml%2Fjump.html
            'loginType':"1",
            'tpl':"mn",
            'callback':"parent.bdPass.api.login._postCallback",
            'username':userInfo["userName"],
            'password':userInfo["passWord"],
            'mem_pass':"on",}
        return  urllib.urlencode(postDict)
    
    
    def getMusicData(self,url):
        '''
        获取百度音乐top100歌曲Url列表
        '''
        request = urllib2.Request(url)
        musicListPage = urllib2.urlopen(request)
        data= musicListPage.read()
        
        
        htmlParser = MyClass()
        #fd = codecs.open("D:/DwonloaderLog.txt")
        htmlParser.feed(data)  #匹配 http://music.baidu.com/top/new的歌曲
        
        onlyLinkTxt = codecs.open(self.currentPath+"/download.txt","w+","utf-8")
        
        musicList = codecs.open(self.currentPath+"/MusicList.html","w+","utf-8")
        
        singerList = codecs.open(self.currentPath+"/singer.txt","w+","utf-8")
        
        songsList = codecs.open(self.currentPath+"/song.txt","w+","utf-8")  #保存歌曲名、歌手名、最终歌曲链接
        
        musicList.write(u" <!DOCTYPE HTML><html><head>风筝-百度音乐抓取器</head><body><ul>")
        #print htmlParser.links
        if htmlParser.links: #歌曲链接
            for kv in htmlParser.links:
                
                #/download?__o=/song/108479485
                musicList.write(u"<li><a href='%s/download?__o=%s'>%s</a>" % (kv[1],kv[2],kv[0]))
                #onlyLinkTxt.write(kv[1]+kv[2]+"\r\n") #只存储链接到本本文件中 以便之后读取下载地址
                onlyLinkTxt.write(u"%s/download?__o=%s\r\n" % (kv[1],kv[2]))
                
        
        if htmlParser.singers: #歌手
            for singer in htmlParser.singers:
                singerList.write(u"%s\r\n" % singer)
                
        if htmlParser.songs:  #歌曲名
            for song in htmlParser.songs:
                songsList.write(u"%s\r\n" % song)
                
        musicList.write("</ul></body></html>")
        musicList.close()
        onlyLinkTxt.close()
        singerList.close()
        songsList.close()
        
    
    def buildMusicList(self):
        '''
        访问top100歌曲url 提取真正的歌曲文件地址
        '''
        mList=codecs.open(self.currentPath+"/download.txt")
        lines= mList.readlines()
        downloadClass = DownloadHTMLParser()
        i=1
        for line in lines:
            if i<=100:
                request= urllib2.Request(line)
                listFile = urllib2.urlopen(request)
                downloadClass.feed(listFile.read())
                i+=1
            
        if downloadClass.mp3_128kbpsFiles:
            self.rowCount=len(downloadClass.mp3_128kbpsFiles)

            self.songAddresses = downloadClass.mp3_128kbpsFiles
   
            mp3UrlList = codecs.open(self.currentPath+"/musicFile.txt","w+","utf-8")
            for mp3File in downloadClass.mp3_128kbpsFiles:

                mp3UrlList.write(mp3File+"\r\n")
        
            
            #mp3UrlList.close()
        else:pass

    
    
    def Login(self,url,username,password):
        nowTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        enter="\r\n"
        logContent = nowTime+enter
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar=cj))
        urllib2.install_opener(opener)
    
        logContent +="Get Cookie"+enter
        request = urllib2.Request(url)
        openRequest = urllib2.urlopen(request)
        for index,cookie in enumerate(cj):
            logContent += "[%s]:%s\r\n" % (index,cookie)
    
        logContent+="Get token"+enter
        tokenUrl = "https://passport.baidu.com/v2/api/?getapi&class=login&tpl=mn&tangram=true"
        tokenRequest = urllib2.urlopen(tokenUrl)
        tokenHtml = tokenRequest.read()
        #reg = re.compile(r"bdPass.api.params.login_token='\w+';")
        reg = re.compile(r"bdPass.api.params.login_token='(?P<tokenVal>\w+)';")
        token = reg.findall(tokenHtml)
        if token:
            tokenVal = token[0]
            logContent +=tokenVal+enter;
    
        logContent +="Login Start"+enter
        baiduMainLoginUrl = "https://passport.baidu.com/v2/api/?login"
        userInfo = {"userName":username,"passWord":password}
        postData =self.BuildPostData(tokenVal,userInfo)
        userAgent ="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.76 Safari/537.36"
        #userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
        baiduRequest = urllib2.Request(baiduMainLoginUrl,postData,headers={"User-Agent":userAgent})
        openBaiduRequest = urllib2.urlopen(baiduRequest)
        baiduPage = openBaiduRequest.read()
       
        logContent+="Login OK Congratulation!"+enter
        
        
        #urlRe = re.compile("encodeURI\\('(?P<fzUrl>\s+)'\\);")
        urlRe = re.compile(r"(?P<URL>http://www.baidu.com/cache/user/html/jump.html\S+)'")
        #TODO:
        #urlRe = re.compile("window.location.replace\\(\\)")
        lastUrl = urlRe.findall(baiduPage)
    
        trueLoginUrl = lastUrl[0]
        logContent+=u"真正登录地址"+trueLoginUrl
        lastRequest = urllib2.Request(trueLoginUrl)
        openLastRequest = urllib2.urlopen(trueLoginUrl)
        
        logContent+="Request the url of http://music.baidu.com/top/new"
        try:
            loginlog =codecs.open(self.currentPath+"\login.log","w+","utf-8")
            loginlog.write(logContent)
            loginlog.close()
        except:
            raise
            loginlog.close()
        
        baiduMusicUrl = "http://music.baidu.com/top/new"
        self.getMusicData(baiduMusicUrl)
        self.buildMusicList()
    
    def translate(self,text):
        _encoding = QApplication.UnicodeUTF8
        return QApplication.translate("MainWindow", text, None, _encoding)
    
    def lastModifyTimeIsToday(self,filename):
        '''
        判断最后修改时间是不是今天
        '''
        lastModifytime = time.strftime("%Y%m%d",time.localtime(os.stat(filename).st_mtime)) 
        timenow=time.strftime("%Y%m%d",time.localtime(time.time()))
        return lastModifytime==timenow
    
    def recordsExistAndLasted(self):
        '''
        判断需要的文件是不是存在  并且是今天产生的 
        '''
        musicfilepath = self.currentPath+"/musicFile.txt"
        singerfilepath = self.currentPath+"/singer.txt"
        songfilepath = self.currentPath+"/song.txt"
        if os.path.exists(musicfilepath) and \
        os.path.exists(singerfilepath) and \
        os.path.exists(songfilepath) and \
        self.lastModifyTimeIsToday(musicfilepath) and \
        self.lastModifyTimeIsToday(singerfilepath) and \
        self.lastModifyTimeIsToday(songfilepath):
            return True
        else:
            return False
        
        
import threading
class DownloadThread(threading.Thread):
    per=0
    def __init__(self,num,interval,kwargs=None):
        super(DownloadThread,self).__init__()
        self.thread_num = num
        self.interval = interval
        self.thread_stop = False
        if not kwargs==None:
            self.songUrl = kwargs[0]
            self.localPath = kwargs[1]
            self.table = kwargs[2]
        
    def run(self):
        #TODO:下载线程
        urllib.urlretrieve(str(self.songUrl), self.localPath, self.downloadCallback)
        #while not self.thread_stop:
            #print "alive"
        
    def downloadCallback(self,a,b,c):
        self.per=100*a*b/c
        if self.per>100:
            self.per = 100
            self.thread_stop = True
            

class login(QDialog):
    CONFIGPATH = os.getcwd()+"\config"
    
    loaderthread = None
    
    listener = None
    def __init__(self,parent=None):
        super(login,self).__init__(parent)
        
        
        self.getDefaultStroagePath()
        self.resize(QSize(378,292))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
                
        self.label_title = QLabel(u"风筝百度音乐下载器")
        self.label_title.setFixedHeight(30)
        
        self.btn_close = QPushButton()
        self.btn_close.setStyleSheet("""QPushButton{background-image:url(./img/btn_close_normal.png);width:39px;height:18px;padding-top:0px;border:0px;} 
                                    QPushButton:hover{background-image:url(./img/btn_close_highlight.png);}
                                    QPushButton:pressed{background-image:url(./img/btn_close_down.png);}""")
        
        self.btn_min = QPushButton()
        self.btn_min.setStyleSheet("QPushButton{background-image:url(./img/btn_close_normal1.png);width:39px;height:18px;padding-top:0px;border:0px;}")
      
        
        self.layout_top = QHBoxLayout() #顶部栏
        self.layout_top.addWidget(self.label_title,1,Qt.AlignLeft)
        self.layout_top.addWidget(self.btn_min,0,Qt.AlignRight | Qt.AlignTop)
        self.layout_top.addWidget(self.btn_close,0,Qt.AlignRight | Qt.AlignTop)

        self.label_loginname = QLabel(u"登录名：")
        self.text_loginname = QLineEdit()
        self.text_loginname.setFixedSize(QSize(230,30))
        #self.text_loginname.setStyleSheet("QLabel{margin:0px 0px 0px 55px;}")
        
        self.layout_loginname = QHBoxLayout()
        self.layout_loginname.addStretch()
        self.layout_loginname.addWidget(self.label_loginname)

        self.layout_loginname.addWidget(self.text_loginname)
        self.layout_loginname.addStretch()
        
        
        self.label_password = QLabel(u" 密码：")
        self.text_password = QLineEdit()
        self.text_password.setEchoMode(QLineEdit.Password)
        
        self.text_password.setFixedSize(QSize(230,30))
        
        self.layout_password = QHBoxLayout()
        self.layout_password.addStretch()
        self.layout_password.addWidget(self.label_password)
        self.layout_password.addWidget(self.text_password)
        self.layout_password.addStretch()
        
        self.btnOk = QPushButton(u"登录")
        self.btnOk.setFixedSize(QSize(120,60))
        
        self.layout_button = QHBoxLayout()
        self.layout_button.addStretch(1)
        self.layout_button.addWidget(self.btnOk)
        self.layout_button.addStretch(1)
        
        
        
        self.layout_main = QVBoxLayout() #整个布局外框
        self.layout_main.addLayout(self.layout_top)
        self.layout_main.addStretch() #平均分配空间
        self.layout_main.addLayout(self.layout_loginname)
        self.layout_main.addStretch() #平均分配空间
        self.layout_main.addLayout(self.layout_password)
        self.layout_main.addStretch() #平均分配空间
        self.layout_main.addLayout(self.layout_button)
        self.layout_main.addStretch() #平均分配空间
        self.setLayout(self.layout_main)
        self.layout_main.setContentsMargins(0,0,0,0)
        self.layout_main.setSpacing(0)
        
        QObject.connect(self.btn_close, SIGNAL("clicked()"),self.LoginExit)
        self.btn_min.clicked.connect(self.mini_click)
        self.connect(self.btnOk, SIGNAL("clicked()"),self.LoginBaidu)
        
        helperModel = helper(None)
        if helperModel.recordsExistAndLasted():
            self.close()
            loaderWindow = Ui_MainWindow(str(self.text_loginname.text()).strip(),str(self.text_password.text()),parent=None)
            loaderWindow.exec_()
        
    def paintEvent(self,event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.drawPixmap(self.rect(), QPixmap("./img/background_blue.png"))
        self.painter.end()
    

    def LoginExit(self):
        #sys.exit()
        self.close()
        
    def mini_click(self):
        self.showMinimized() 
    
    def LoginBaidu(self):
        if str(self.text_loginname.text()).strip()!='' and self.text_password.text()!='':          
            self.btnOk.setText(u'请耐心等待...')
            helperModel = helper(None)
            if not helperModel.recordsExistAndLasted():
                
                try:
                    if self.Login("http://wwww.baidu.com"):
                        self.close()
                        loaderWindow = Ui_MainWindow(str(self.text_loginname.text()).strip(),str(self.text_password.text()),parent=None)
                        loaderWindow.exec_()
                        
                    else:
                        QMessageBox.warning(self,u'登录失败',u'可能是用户名或密码有问题',QMessageBox.Yes)
                        self.btnOk.setText(u"再次登录")
                except:
                    raise
                    self.btnOk.setText(u"再次登录")
                    return
            else:
                self.close()
                loaderWindow = Ui_MainWindow(str(self.text_loginname.text()).strip(),str(self.text_password.text()),parent=None)
                loaderWindow.exec_()
                  
                
    
    def getDefaultStroagePath(self):
        try:
            if not os.path.exists(self.CONFIGPATH):
                os.mkdir(self.CONFIGPATH)
        except:
            pass
            
    def threadLogin(self):
        helperModel = helper(None)
        if not helperModel.recordsExistAndLasted():
            helperModel.Login("http://www.baidu.com",str(self.text_loginname.text()).strip(),str(self.text_password.text()))
            
                            
            
    def listen(self):
        print "time3"
        if self.loaderthread!=None and not self.loaderthread.is_alive():
            loaderWindow = Ui_MainWindow()
            loaderWindow.exec_()
            self.close()
        self.listener = threading.Timer(3,self.listen)
        self.listener.setDaemon(True)   
        self.listener.start()
          
    def Login(self,url):
        nowTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        enter="\r\n"
        logContent = nowTime+enter
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar=cj))
        urllib2.install_opener(opener)
    
        logContent +="Get Cookie"+enter
        request = urllib2.Request(url)
        openRequest = urllib2.urlopen(request)
        for index,cookie in enumerate(cj):
            logContent += "[%s]:%s\r\n" % (index,cookie)
    
        logContent+="Get token"+enter
        tokenUrl = "https://passport.baidu.com/v2/api/?getapi&class=login&tpl=mn&tangram=true"
        tokenRequest = urllib2.urlopen(tokenUrl)
        tokenHtml = tokenRequest.read()
        #reg = re.compile(r"bdPass.api.params.login_token='\w+';")
        reg = re.compile(r"bdPass.api.params.login_token='(?P<tokenVal>\w+)';")
        token = reg.findall(tokenHtml)
        if token:
            tokenVal = token[0]
            logContent +=tokenVal+enter;

        logContent +="Login Start"+enter
        baiduMainLoginUrl = "https://passport.baidu.com/v2/api/?login"
        userInfo = {"userName":str(self.text_loginname.text()),"passWord":str(self.text_password.text())}
        postData =self.BuildPostData(tokenVal,userInfo)
        userAgent ="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.76 Safari/537.36"
        #userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
        baiduRequest = urllib2.Request(baiduMainLoginUrl,postData,headers={"User-Agent":userAgent})
        openBaiduRequest = urllib2.urlopen(baiduRequest)
        baiduPage = openBaiduRequest.read()
        
        personCenter = urllib2.urlopen("http://i.baidu.com/")
        if personCenter.read().find("header-tuc-uname")>-1:
            logContent+="Login OK Congratulation!"+enter
            return True
        else:
            #print "登录失败"
            logContent+="Login faild!"+enter
            return False
        f = codecs.open("d:\log1.txt", "w+","utf-8")   
        f.write(logContent)
        f.close()
        
 
    def BuildPostData(self,token,userInfo):
        jumppage = "http://www.baidu.com/cache/user/html/jump.html"

        postDict = {
            'charset':"utf-8",
            'token':token, #de3dbf1e8596642fa2ddf2921cd6257f
            'isPhone':"false",
            'index':"0",
            'staticpage':jumppage, #http%3A%2F%2Fwww.baidu.com%2Fcache%2Fuser%2Fhtml%2Fjump.html
            'loginType':"1",
            'tpl':"mn",
            'callback':"parent.bdPass.api.login._postCallback",
            'username':userInfo["userName"],
            'password':userInfo["passWord"],
            'mem_pass':"on",}
        return  urllib.urlencode(postDict)
    
    

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

#TODO:主窗体
class Ui_MainWindow(QtGui.QDialog):
    
    CONFIGPATH = os.getcwd()+"\config"
    
    DEFAUTMUSICPATH = os.getcwd()+"\music"
    #===========================================================================
    # 标识是否继续下载 用于批量下载
    #===========================================================================
    continueDownload = True
    
    #===========================================================================
    # 待下载歌单队列
    #===========================================================================
    songsMenu = None
    
    username = ''
    password = ''
    
    def __init__(self,username,password,parent=None):
        super(Ui_MainWindow,self).__init__(parent)
        try:
            if not os.path.exists(self.DEFAUTMUSICPATH):
                os.mkdir(self.DEFAUTMUSICPATH)
        except:raise
        
        self.username = username
        self.password = password
        self.stroagePath = self.getDefaultStroagePath()
        self.setupUi(self)
        

        #self.settingWindow = settingDig(self)
        
        
    
    
    def getDefaultStroagePath(self):
        sPath = self.DEFAUTMUSICPATH
        try:
            if not os.path.exists(self.CONFIGPATH):
                os.mkdir(self.CONFIGPATH)
            else:
                f = codecs.open(self.CONFIGPATH+"\config.pkd")
                sPath = f.read()
        except:
            sPath = self.DEFAUTMUSICPATH
        return sPath
    
    def createDataWidget(self):
        helperModel = helper(None)
        
        if not helperModel.recordsExistAndLasted():
            helperModel.Login("http://www.baidu.com",self.username,self.password)
            
            
        #self.buildMusicList()
        musiczipfile = codecs.open(helperModel.currentPath+"/musicFile.txt")
        singerfile = codecs.open(helperModel.currentPath+"/singer.txt")
        songfile=codecs.open(helperModel.currentPath+"/song.txt")
        musiczipfilelines = musiczipfile.readlines()
        rowcount = len(musiczipfilelines)
        
        table = QTableWidget(rowcount,6)
        table.setEditTriggers(
            QtGui.QAbstractItemView.DoubleClicked |
            QtGui.QAbstractItemView.SelectedClicked)
        table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        table.setHorizontalHeaderLabels([u"歌名",u"歌手",u'url',u"", u'',''])
       
        rowNumber = 0
        for song,singer,url in zip(songfile.readlines(),singerfile.readlines(),musiczipfilelines):
            item1 = QTableWidgetItem(helperModel.translate(song))
            item2 = QTableWidgetItem(helperModel.translate(singer))
            item3 = QTableWidgetItem(helperModel.translate(url))
            item4 = QTableWidgetItem()
            item4.setCheckState(0) 
            
            #item4.setCheckable(True) 
            item5 = QTableWidgetItem()
            #item5.setData(0, [song,singer,url])
            
            item6Progress = QTableWidgetItem()
            

            #item5.setData(0,True)
            table.setItem(rowNumber,0,item1)
            table.setItem(rowNumber,1,item2)
            table.setItem(rowNumber,2,item3)
            table.setItem(rowNumber,3,item4)
            table.setItem(rowNumber,4,item5)
            table.setItem(rowNumber,5,item6Progress)
            
            btn = fzDownloadButton(parent=table,rowNum=rowNumber,columnNum=4)
            table.setCellWidget(rowNumber,4,btn)
            
            #下载进度条
            progressBar = QtGui.QProgressBar()
            progressBar.setVisible(False)
            progressBar.setMaximum(100)
            
            progressBar.setStyleSheet('''QProgressBar {border: 2px solid grey;border-radius: 5px;text-align: center;}
                                         QProgressBar::chunk {background-color: #05B8CC;width: 10px;margin:0.5px;}''')
            table.setCellWidget(rowNumber,5,progressBar)
            table.connect(btn,SIGNAL("downloadclick(int , int)"),self.downLoad_click_thread)
           
            rowNumber+=1
           
        
        table.resizeColumnsToContents()
        table.setColumnHidden(2,True)
        table.setGeometry(80, 20, 400, 300)
        musiczipfile.close()
        singerfile.close()
        songfile.close()
        table.setObjectName(_fromUtf8("tableView"))
        return table
        
    
        
    def downloadCallback(self,a,b,c):
        per=100*a*b/c
        if per>100:
            per = 100
        self.table.cellWidget(self.curDownloadRowNum, 5).setValue(per)
        
    curDownloadRowNum = 0
    def downLoad_click(self,row,column):
        songTitle =self.table.item(row, 0).text()
        singer = self.table.item(row, 1).text()
        songUrl = self.table.item(row, 2).text()
        helperModel = helper(None)
        
        #QtGui.QMessageBox.information(None, u"tips",u"%s，%s,%s" % (songTitle,singer,songUrl))
        self.curDownloadRowNum = row
        localPath ="%s%s%s" % (self.stroagePath+"/",_fromUtf8((str(songTitle)).strip()),".mp3")
        urllib.urlretrieve(str(songUrl), localPath, self.downloadCallback)
        
    def downLoad_click_thread(self,row,column):
        songTitle =self.table.item(row, 0).text()
        singer = self.table.item(row, 1).text()
        songUrl = self.table.item(row, 2).text()
        helperModel = helper(None)
        
        self.curDownloadRowNum = row
        localPath ="%s%s%s" % (self.stroagePath+"/",_fromUtf8((str(songTitle)).strip()),".mp3")
    
        #urllib.urlretrieve(str(songUrl), localPath, self.downloadCallback)
        self.lock = RLock()
        thread = Thread(target=self.download(songUrl,localPath))
        thread.setDaemon(True)
        thread.start()
    
    def download(self,songUrl,localPath):
        try:
            urllib.urlretrieve(str(songUrl),localPath,self.downloadCallback)
        except:pass
        
    

    
    def batchdownload_click(self):
        self.sender().setEnabled(False)
        threadNum = 5 #开启下载的线程数
        self.songsMenu = Queue()
        self.lock = RLock()
        rowCount = self.table.rowCount()
        for row in range(rowCount):
            if self.table.item(row, 3).checkState()>0: #获取地4列的内容 直接当做QChecbox使用
                #添加到批量下载歌单中：[[歌名,歌手,url],[歌名,歌手,url]] 可以复制所有链接 粘贴到迅雷等下载工具中 批量下载
                #songsMenu.append([self.table.item(row, 0).text(),self.table.item(row, 1).text(),self.table.item(row, 2).text()])
                #self.table.cellWidget(row, 4).click() #模拟点击下载按钮
                self.songsMenu.put([self.table.item(row, 0).text(),self.table.item(row, 1).text(),self.table.item(row, 2).text(),row])
        pool = []
        for _ in range(threadNum):
            pool.append(Thread(target=self.batchdownload()))
            pool[-1].setDaemon(True)
            pool[-1].start()
            
    
    def batchdownload(self): 
        while not self.songsMenu.empty():
            self.lock.acquire()
            songinfo = self.songsMenu.get()
            self.lock.release()
            songTitle = songinfo[0]
            singer = songinfo[1]
            url = songinfo[2]
            row = songinfo[3]
            self.curDownloadRowNum = row
            localPath ="%s%s%s" % (self.stroagePath+"/",_fromUtf8((str(songTitle)).strip()),".mp3")
            self.download(url, localPath)
            self.songsMenu.task_done()
        else:
            self.btn_batchDownload.setEnabled(True)
    
    def copyToBoard(self):
        rowCount = self.table.rowCount()
        urls = []
        for row in range(rowCount):
            if self.table.item(row, 3).checkState()>0:
                urls.append(str(self.table.item(row, 2).text()))
        board = linkboard(' '.join(urls))
        board.exec_()
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(767, 584)
        MainWindow.setWindowFlags(Qt.FramelessWindowHint)
        
        #=======================================================================
        # 顶部操作栏 
        #=======================================================================
        self.btn_close = QPushButton()
        self.connect(self.btn_close, SIGNAL("clicked()"),self.exitMianwindow)
        self.btn_close.setStyleSheet("""QPushButton{background-image:url(./img/btn_close_normal.png);width:39px;height:18px;padding-top:0px;border:0px;} 
                                    QPushButton:hover{background-image:url(./img/btn_close_highlight.png);}
                                    QPushButton:pressed{background-image:url(./img/btn_close_down.png);}""")
        
        self.btn_min = QPushButton()
        self.connect(self.btn_min, SIGNAL("clicked()"),self.minWindow)
        self.btn_min.setStyleSheet("QPushButton{background-image:url(./img/btn_close_normal1.png);width:39px;height:18px;padding-top:0px;border:0px;}")
        
        self.btn_setting = QPushButton()
        self.connect(self.btn_setting,SIGNAL("clicked()"),self.setting_click)
        self.btn_setting.setStyleSheet("""QPushButton{background-image:url(./img/icon_cog.png);width:16px;height:16px;padding-top:0px;border:0px;margin-right:15px;}
                                        QPushButton:hover{background-image:url(./img/icon_cogs.png);}""")
        
        self.btn_photo = QPushButton()
        self.btn_photo.setStyleSheet("""QPushButton{background-image:url(./img/photo.png);width:32px;height:32px; border-radius: 10px;
                                        margin-right:15px;}""")
        
        self.topBarLayout = QtGui.QHBoxLayout()
        self.topBarLayout.addStretch()
        self.topBarLayout.addWidget(self.btn_photo,0,Qt.AlignRight | Qt.AlignHCenter)
        self.topBarLayout.addWidget(self.btn_setting,0,Qt.AlignRight | Qt.AlignHCenter)
        self.topBarLayout.addWidget(self.btn_min,0,Qt.AlignRight | Qt.AlignTop)
        self.topBarLayout.addWidget(self.btn_close,0,Qt.AlignRight | Qt.AlignTop)
        
        #=======================================================================
        # 列表区域  TODO:定制列表样式
        #=======================================================================
        self.table = self.createDataWidget()
        #self.table.setStyleSheet("QWidget{background:url(./img/mianbg.png);}")
        self.listLayout = QtGui.QHBoxLayout()
        self.listLayout.addWidget(self.table)
        
        #=======================================================================
        # 底部操作栏
        #=======================================================================
        self.btn_batchDownload = QtGui.QPushButton(u"批量下载")
        self.connect(self.btn_batchDownload, SIGNAL('clicked()'),self.batchdownload_click)
        self.btn_copytoboard = QtGui.QPushButton(u"复制链接")
        self.connect(self.btn_copytoboard,SIGNAL("clicked()"),self.copyToBoard)
        self.btn_copytoboard.setToolTip(u"利用复制链接功能，将所选歌曲链接复制到剪切板，可在下载工具（如迅雷）中新建任务，直接粘贴即可实现批量下载。")
        self.checkall = QtGui.QCheckBox(u'全选')
        self.connect(self.checkall,SIGNAL("stateChanged(int)"),self.checkall_click)
        
        self.bottomBarLayout = QtGui.QHBoxLayout()
        self.bottomBarLayout.addStretch()
        self.bottomBarLayout.addWidget(self.checkall,0,Qt.AlignRight)
        self.bottomBarLayout.addWidget(self.btn_copytoboard,0,Qt.AlignRight)
        self.bottomBarLayout.addWidget(self.btn_batchDownload,0,Qt.AlignRight)
        
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addLayout(self.topBarLayout,0)
        self.mainLayout.addStretch()
        self.mainLayout.addLayout(self.listLayout,1)
        self.mainLayout.addStretch()
        self.mainLayout.addLayout(self.bottomBarLayout,1)
        self.setLayout(self.mainLayout)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        

    def paintEvent(self,event):
        self.painter = QtGui.QPainter()
        self.painter.begin(self)
        self.painter.drawPixmap(self.rect(), QPixmap("./img/mianbg.png"))
        self.painter.end()
    def checkall_click(self,state):
        rowCount = self.table.rowCount()
        if state==2:
            for i in range(rowCount):
                self.table.item(i, 3).setCheckState(2)
        else:
            for i in range(rowCount):
                self.table.item(i, 3).setCheckState(False)
                
    def setting_click(self):
        self.settingWindow = settingDig(self.stroagePath,parent=self)
        self.settingWindow.exec_()
        
    def minWindow(self):
        self.showMinimized()
        
    def exitMianwindow(self):
        sys.exit()
        
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "百度音乐下载器 ", None))
        self.label.setText(_translate("MainWindow", "头像", None))
        self.label_2.setText(_translate("MainWindow", "登录名称", None))
        self.pushButton.setText(_translate("MainWindow", "PushButton", None))


class settingDig(QtGui.QDialog):
    def __init__(self,argv='',parent=None):
        super(settingDig,self).__init__(parent)
        self.resize(QtCore.QSize(378,292))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        
        self.label_title = QtGui.QLabel(u"设置")
        self.label_title.setFixedHeight(30)
        
        self.btn_close = QtGui.QPushButton()
        self.btn_close.setStyleSheet("""QPushButton{background-image:url(./img/btn_close_normal.png);width:39px;height:18px;padding-top:0px;border:0px;} 
                                    QPushButton:hover{background-image:url(./img/btn_close_highlight.png);}
                                    QPushButton:pressed{background-image:url(./img/btn_close_down.png);}""")
        
        
        self.layout_top = QtGui.QHBoxLayout() #顶部栏
        self.layout_top.addWidget(self.label_title,1,QtCore.Qt.AlignLeft)
        self.layout_top.addWidget(self.btn_close,0,QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)

        self.label_loginname = QtGui.QLabel(u"存储路径：")
        self.text_storage = QtGui.QLineEdit()
        self.text_storage.setText(argv)
        self.text_storage.setFixedSize(230,30)
        self.btn_settingStoragePath = QtGui.QPushButton(u"设置默认存储位置")
        self.connect(self.btn_settingStoragePath,QtCore.SIGNAL("clicked()"),self.settingStorage_click)
        
        self.layout_loginname = QtGui.QVBoxLayout()
        self.layout_title = QtGui.QHBoxLayout()
        self.layout_loginname.addStretch()
        
        self.layout_loginname.addWidget(self.label_loginname)
        self.layout_title.addWidget(self.text_storage)
        self.layout_loginname.addStretch()
        self.layout_title.addWidget(self.btn_settingStoragePath)
        self.layout_loginname.addLayout(self.layout_title)
        
        
        
        self.btnOk = QtGui.QPushButton(u"保存")
        self.btnOk.setFixedSize(120,30)
        
        self.layout_button = QtGui.QHBoxLayout()
        self.layout_button.addStretch(1)
        self.layout_button.addWidget(self.btnOk)
        self.layout_button.addStretch(1)
        
        
        
        self.layout_main = QtGui.QVBoxLayout() #整个布局外框
        self.layout_main.addLayout(self.layout_top)
        self.layout_main.addStretch() #平均分配空间
        self.layout_main.addLayout(self.layout_loginname)
        self.layout_main.addStretch() #平均分配空间
       
        self.layout_main.addLayout(self.layout_button)
        self.layout_main.addStretch() #平均分配空间
        self.setLayout(self.layout_main)
        self.layout_main.setContentsMargins(0,0,0,0)
        self.layout_main.setSpacing(0)
        
        self.connect(self.btn_close, QtCore.SIGNAL("clicked()"),self.LoginExit)
        self.connect(self.btnOk, QtCore.SIGNAL("clicked()"),self.LoginBaidu)
        
        
    def paintEvent(self,event):
        self.painter = QtGui.QPainter()
        self.painter.begin(self)
        self.painter.drawPixmap(self.rect(), QtGui.QPixmap("./img/show_con_bg.jpg"))
        self.painter.end()
    

    def settingStorage_click(self):
        folder = QtGui.QFileDialog.getExistingDirectory(None,u"默认存储",os.getcwd())
        self.text_storage.setText(folder)
        
    
    def LoginExit(self):
        self.close()
    
    def LoginBaidu(self):
        storagepath = self.text_storage.text()
        if not os.path.exists(storagepath):        
            try:
                os.mkdir(storagepath)
            except:
                QtGui.QMessageBox.warning(self, u'路径错误', u'非法路径')
                return
        
        iniconfig = codecs.open(os.getcwd()+"\config"+"\config.pkd","w", "utf-8")
        iniconfig.write(storagepath)
        iniconfig.close()
        self.parent().stroagePath = storagepath
        self.close()
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = login()
    dialog.show()
    sys.exit(app.exec_())