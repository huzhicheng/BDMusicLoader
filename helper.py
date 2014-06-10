# -*- coding: utf-8 -*-
'''
Created on 2014年2月17日

@author: huzhicheng
'''
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import urllib,urllib2,cookielib,re,codecs
from bdMusicHtmlParser import MyClass
from bdMusicHtmlParser import DownloadHTMLParser
import os,time
import setting

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
        
        musicList.write(u"<!DOCTYPE HTML><html><head>风筝-百度音乐抓取器</head><body><ul>")
        #print htmlParser.links
        if htmlParser.links: #歌曲链接
            for kv in htmlParser.links:
                
                #/download?__o=/song/108479485
                #print chardet.detect(kv[0])
                musicList.write("<li><a href='%s/download?__o=%s'>%s</a>" % (kv[1],kv[2],kv[0].decode("utf8")))
                #onlyLinkTxt.write(kv[1]+kv[2]+"\r\n") #只存储链接到本本文件中 以便之后读取下载地址
                onlyLinkTxt.write("%s/download?__o=%s\r\n" % (kv[1],kv[2].decode("utf8")))
                
        
        if htmlParser.singers: #歌手
            for singer in htmlParser.singers:
                singerList.write("%s\r\n" % singer.decode("utf8"))
                
        if htmlParser.songs:  #歌曲名
            for song in htmlParser.songs:
                songsList.write("%s\r\n" % song.decode("utf8"))
        musicList.write("</ul></body></html>")
        musicList.close()
        onlyLinkTxt.close()
        singerList.close()
        songsList.close()
        print "End"
        
    
    def buildMusicList(self):
        '''
        访问top100歌曲url 提取真正的歌曲文件地址
        '''
        mList=codecs.open(self.currentPath+"/download.txt")
        lines= mList.readlines()
        downloadClass = DownloadHTMLParser()
        i=1
        for line in lines:
            print line
            print i
            if i<=100:
                request= urllib2.Request(line)
                listFile = urllib2.urlopen(request)
                content = listFile.read()
                downloadClass.feed(content.decode("utf8"))
                i=i+1


        print downloadClass.mp3_128kbpsFiles
        if downloadClass.mp3_128kbpsFiles:
            self.rowCount=len(downloadClass.mp3_128kbpsFiles)
            print "len(downloadClass.mp3_128kbpsFiles)",len(downloadClass.mp3_128kbpsFiles)
            
            self.songAddresses = downloadClass.mp3_128kbpsFiles
            print self.rowCount,len(downloadClass.mp3_128kbpsFiles)
            print "len(downloadClass.mp3_128kbpsFiles)",len(downloadClass.mp3_128kbpsFiles)
            mp3UrlList = codecs.open(self.currentPath+"/musicFile.txt","w+","utf-8")
            for mp3File in downloadClass.mp3_128kbpsFiles:
                mp3UrlList.write(mp3File+"\r\n")
            
            
            #mp3UrlList.close()
        else:print "have no data"

        print "End"
    
    
    def Login(self,url):
        nowTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        enter="\r\n"
        logContent = nowTime+enter
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar=cj))
        urllib2.install_opener(opener)
    
        print "Get Cookie"
        logContent +="Get Cookie"+enter
        request = urllib2.Request(url)
        openRequest = urllib2.urlopen(request)
        for index,cookie in enumerate(cj):
            print "[%s]:%s\r\n" % (index,cookie)
            logContent += "[%s]:%s\r\n" % (index,cookie)
    
        print "Get token"
        logContent+="Get token"+enter
        tokenUrl = "https://passport.baidu.com/v2/api/?getapi&class=login&tpl=mn&tangram=true"
        tokenRequest = urllib2.urlopen(tokenUrl)
        tokenHtml = tokenRequest.read()
        #reg = re.compile(r"bdPass.api.params.login_token='\w+';")
        reg = re.compile(r"bdPass.api.params.login_token='(?P<tokenVal>\w+)';")
        token = reg.findall(tokenHtml)
        if token:
            tokenVal = token[0]
            print tokenVal
            logContent +=tokenVal+enter;
    
        print "登录成功"
        logContent +="Login Start"+enter
        baiduMainLoginUrl = "https://passport.baidu.com/v2/api/?login"
        print setting.username
        userInfo = {"userName":setting.username,"passWord":setting.password}
        postData =self.BuildPostData(tokenVal,userInfo)
        userAgent ="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.76 Safari/537.36"
        #userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
        baiduRequest = urllib2.Request(baiduMainLoginUrl,postData,headers={"User-Agent":userAgent})
        openBaiduRequest = urllib2.urlopen(baiduRequest)
        baiduPage = openBaiduRequest.read()
       
        personCenter = urllib2.urlopen("http://i.baidu.com/")
        if personCenter.read().find("header-tuc-uname")>-1:
            print "Login OK Congratulation!"
            logContent+="Login OK Congratulation!"+enter
    
        else:
            print "Login fail"
            return
        
        
        #urlRe = re.compile("encodeURI\\('(?P<fzUrl>\s+)'\\);")
        urlRe = re.compile(r"(?P<URL>http://www.baidu.com/cache/user/html/jump.html\S+)'")
        #TODO:
        #urlRe = re.compile("window.location.replace\\(\\)")
        lastUrl = urlRe.findall(baiduPage)
        if lastUrl:
            print lastUrl[0]
    
        trueLoginUrl = lastUrl[0]
        logContent+=u"真正登录地址"+trueLoginUrl
        lastRequest = urllib2.Request(trueLoginUrl)
        openLastRequest = urllib2.urlopen(trueLoginUrl)
        print openLastRequest.geturl()
        
        logContent+="Request the url of"+setting.musiclistUrl
        try:
            loginlog =codecs.open(self.currentPath+"\login.log","w+","utf-8")
            loginlog.write(logContent)
            loginlog.close()
        except:
            raise
            loginlog.close()
        
        baiduMusicUrl = setting.musiclistUrl
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