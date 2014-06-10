#encoding=utf-8
'''
Created on 2014

@author: huzhicheng
'''

from HTMLParser import HTMLParser
import re

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
            print data

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
                    print attrs
                    link = "http://music.baidu.com%s" % (value)
                    if link not in self.mp3_128kbpsFiles:
                        self.mp3_128kbpsFiles.append("http://music.baidu.com%s" % (value))
                        print i
                        i+=1
                    
                    
    
#     def handle_endtag(self,tag):
#         if tag=="a" and self.curTag:
#             for name,value in self.curTag:
#                 if name=="href":
#                     self.mp3_128kbpsFiles.append("http://music.baidu.com%s" % (value))
                    
                    
                    
                    
                    
                        
                    
                
                    
            