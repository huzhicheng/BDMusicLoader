__author__ = 'huzhicheng'
import urllib,urllib2,cookielib,re,codecs

def BuildPostData(token,userInfo):
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

def Login(url):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar=cj))
    urllib2.install_opener(opener)

    print "Get Cookie"
    request = urllib2.Request(url)
    openRequest = urllib2.urlopen(request)
    for index,cookie in enumerate(cj):
        print "[%s]:%s\r\n" % (index,cookie)

    print "Get token"
    tokenUrl = "https://passport.baidu.com/v2/api/?getapi&class=login&tpl=mn&tangram=true"
    tokenRequest = urllib2.urlopen(tokenUrl)
    tokenHtml = tokenRequest.read()
    #reg = re.compile(r"bdPass.api.params.login_token='\w+';")
    reg = re.compile(r"bdPass.api.params.login_token='(?P<tokenVal>\w+)';")
    token = reg.findall(tokenHtml)
    if token:
        tokenVal = token[0]
        print tokenVal

    print "oh yeah Login Start"
    baiduMainLoginUrl = "https://passport.baidu.com/v2/api/?login"
    userInfo = {"userName":"","passWord":""}
    postData = BuildPostData(tokenVal,userInfo)
    userAgent ="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.76 Safari/537.36"
    baiduRequest = urllib2.Request(baiduMainLoginUrl,postData,headers={"User-Agent":userAgent})
    openBaiduRequest = urllib2.urlopen(baiduRequest)
    baiduPage = openBaiduRequest.read()
    print baiduPage
    baiduHtmlFile = codecs.open("d:/baidu.html","w+","utf-8")
    baiduHtmlFile.write(baiduPage)
    baiduHtmlFile.close()

    print "Login OK Congratulation!"
    print r"d:\baidu.html"

    #urlRe = re.compile("encodeURI\\('(?P<fzUrl>\s+)'\\);")
    urlRe = re.compile(r"(?P<URL>http://www.baidu.com/cache/user/html/jump.html\S+)'")
    #TODO:
    #urlRe = re.compile("window.location.replace\\(\\)")
    lastUrl = urlRe.findall(baiduPage)
    if lastUrl:
        print lastUrl[0]

    trueLoginUrl = lastUrl[0]
    lastRequest = urllib2.Request(trueLoginUrl)
    openLastRequest = urllib2.urlopen(trueLoginUrl)
    print openLastRequest.geturl()

    tiebaRequest = urllib2.Request("http://tieba.baidu.com/")
    openTiebaRequest = urllib2.urlopen(tiebaRequest)
    content = openTiebaRequest.read()
    fd = codecs.open(r"d:\tiebao.html","w+")
    fd.write(content)
    fd.close()



if __name__=="__main__":
    url = "http://www.baidu.com"
    Login(url)
