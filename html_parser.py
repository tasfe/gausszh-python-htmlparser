#!/usr/bin/env python
#coding=utf8
#按类别收集，多线程,更完善的错误处理（网络连接错误）
#E-mail:gauss.zh@gmail.com
import urllib2
import re
import time
import json
import getAllUrl
from sgmllib import SGMLParser
from Queue import Queue
import threading
urlpat=re.compile(r'\.*itunes.apple.com/us/app.*id.*\d')
category=''
queue=Queue()
errorqueue=Queue()
class ListName(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.infoFlag = ""
        self.appurl=[]
        self.appname=[]
        self.descriptionFlag=''
        self.descriptionPFlag=''
        self.description=[]
        self.appnameFlag=''
        self.info=[]
        self.iphonescreenshots=[]
        self.ipadscreenshots=[]
        self.whatisnewFlag=''
        self.whatisnew=[]
        self.allstartFlag=''
        self.allstart=[]
        self.customerstartFlag=''
        self.customerstart=[]
        self.customerFlag=''
        self.customer=[]
        self.iphonescreenshotsFlag=''
        self.ipadscreenshotsFlag=''
        self.nameFlag=''
        self.name=''
    def handle_data(self, text):
        if self.infoFlag == 1:
            self.info.append(text)
        if self.appnameFlag==1:
            self.appname.append(text)
            self.appnameFlag=''
        if self.descriptionFlag==1 and self.descriptionPFlag==1 :
            self.description.append(text)     
        if self.customerFlag==1:
            self.customer.append(text)
        if self.whatisnewFlag==1:
            self.whatisnew.append(text)
        if self.nameFlag==1:
            self.name+=text
    def start_p(self,attrs):
        if self.descriptionFlag==1:
            self.descriptionPFlag=1
    def end_p(self):
        self.descriptionFlag=''
        self.descriptionPFlag=''
    def start_img(self,attrs):
        for n,k in attrs:
            if (k=='landscape' or k=='portrait'):
                if self.ipadscreenshotsFlag==1:
                    self.ipadscreenshots.append(attrs[2][1])
                if self.iphonescreenshotsFlag==1:
                    self.iphonescreenshots.append(attrs[2][1])
            
    def start_a(self,attrs):
        for n,k in attrs:
            if n=='href':
                if re.findall(r'\.*itunes.apple.com/us/app.*id.*\d',k):
                    self.appurl.append(k)
                    self.appnameFlag=1
    def start_div(self,attrs):
        for n,k in attrs:
            if n=='metrics-loc' and k=='Titledbox_Description':#http://itunes.apple.com/us/genre/ios-games/id6014?mt=8
                self.descriptionFlag=1#http://itunes.apple.com/us/app/angry-birds/id343200656?mt=8
            if n=='id' and k=='left-stack':
                self.infoFlag=1
                self.customerFlag=''
            if n=='metrics-loc':
                if re.findall(r"What's New",k):
                    self.whatisnewFlag=1
            if n=='class' and k=='rating' and self.infoFlag==1:
                self.allstart.append(attrs[3][1])
                self.customerstartFlag=1
                self.allstartFlag=1
            if n=='class' and k=='customer-reviews':
                self.customerFlag=1
            if n=='class' and k=='rating' and self.customerFlag==1:
                self.customerstart.append(attrs[3][1])
            if n=='class' :
                if re.findall(r'iphone-screen-shots',k):
                    self.iphonescreenshotsFlag=1
                    self.ipadscreenshotsFlag=''
            if n=='class' :
                if re.findall(r'ipad-screen-shots',k):
                    self.ipadscreenshotsFlag=1
                    self.iphonescreenshotsFlag=''  
    def start_h1(self,attrs):
        self.nameFlag=1  
    def end_h1(self):
        self.nameFlag=''
    def end_div(self):
        self.whatisnewFlag=''
def simplify(lt):
    """去除list中的杂项，比如\n,' '"""
    ret=[]
    for one in lt:
        temp=one.strip()
        if temp:
            ret.append(temp)
    return ret
   
def main():    
    try:
#        (a,b)=getAllUrl.main('http://itunes.apple.com/us/genre/ios-music/id6011?mt=8')
#        urlfile=open('appurl.txt','w')
#        namefile=open('appname.txt','w')
#        a=json.dumps(a)
#        b=json.dumps(b)
#        print >>urlfile,a
#        print >>namefile,b
#        urlfile.close()
#        namefile.close()
        
#        global queue
#        logfile=open('F_starerrornameandurl.txt','r')
#        log=logfile.readlines()
#        logfile.close()
#        for one in log:
#            url=re.findall(r'http.*mt=8',one)[0]
#            n='null'
#            queue.put((n,url))
            
        appnamefile=open('socialnetworkingappname.txt','r')
        appname=json.load(appnamefile)
        appurlfile=open('socialnetworkingappurl.txt','r')
        appurl=json.load(appurlfile)
        appnamefile.close()
        appurlfile.close()
        for i in range(len(appname)):
            n=appname[i]
            u=appurl[i]
            queue.put((n,u))# (name url) tuple
        templatefile=open('template.xml','r')
        template=''.join(templatefile.readlines())
        templatefile.close()
    except Exception,e:
       print str(e)
    threadone=threading.Thread(target=threaddownload,args=('socialnetworking/threadone',template,))
    threadtwo=threading.Thread(target=threaddownload,args=('socialnetworking/threadtwo',template,))
    threadthree=threading.Thread(target=threaddownload,args=('socialnetworking/threadthree',template,))
    threadfour=threading.Thread(target=threaddownload,args=('socialnetworking/threadfour',template,))
    thread5=threading.Thread(target=threaddownload,args=('socialnetworking/threadfive',template,))
    threadone.start()
    threadtwo.start()
    
    threadthree.start()
    threadfour.start()
    thread5.start()
    threadone.join()
    threadtwo.join()
    threadthree.join()          
    threadfour.join()    
    thread5.join()   
#    threaddownload('musicData/123/logF_starthreadfive',template,)
                       
def threaddownload(filename,template):
    global queue
    global errorqueue
    timeoutcounts=0
    outputFile=open(filename+'.xml','w')
    print >>outputFile,'<apps>'
    i=-1
    counts=0
    while True:
        i+=1
        if queue.empty():
            break    
        try:
            (name,url)=queue.get()
            while  True:
                try:                    
                    returnfile=urllib2.urlopen(url,timeout=5)
                    content=returnfile.read()
                    returnfile.close()
                    timeoutcounts=0
                    break
                except Exception,e:
                    if timeoutcounts<5:
                        timeoutcounts+=1                       
                        time.sleep(timeoutcounts)
                    else:
                        print name,url
                        print e
                        errorqueue.put((name,url))
                        break
            if timeoutcounts>=5:
                timeoutcounts=0
                continue    
            listname=ListName()
            listname.feed(content)
#            name=re.findall(r'app/.*/id',appurl[i])[0]
#            name=name[4:-3]
            name=listname.name
            info={}
            j=0
            tmpinfo=simplify(listname.info[0:50])
        
            info['price']='Free'  
            for one in tmpinfo:
                if re.findall(r'\$\d*',one):
                    info['price']=one
                if one in ['Category:','Released','Updated:','Version:','Size:','Languages:','Language:',\
                           'Seller:','Requirements:','Released:','All Versions:','Current Version:']:
                    info[one]=tmpinfo[j+1]
                    if one=='Seller:':
                        info['copyright:']=tmpinfo[j+2]
                        info['app_rating:']=tmpinfo[j+3]
                        info['reasons:']=tmpinfo[j+4]
                j+=1          
#            if locals().has_key('category'):
#                if category!=info['Category:']:
#                    continue
#            else:
            category=info['Category:'] 
            id=str(re.findall(r'[\d]{5,}',url)[0])   
            customer=simplify(listname.customer)
            price=info['price']            
            if info.has_key('Released:'):
                Updated=info['Released:']
            elif info.has_key('Updated:'):
                Updated=info['Updated:']
            version=info['Version:']
            size=info['Size:']
            languages=''
            if info.has_key('Languages:'):
                languages=info['Languages:']
            elif info.has_key('Language:'):
                languages=info['Language:']
            
            seller=info['Seller:']
            copyright=info['copyright:']
            app_rating=info['app_rating:']
            reason=info['reasons:']
            requirements=info['Requirements:']
            stars1=rating_counts1=''
            tmpi=0
            if info.has_key('Current Version:'):
                t=listname.allstart[tmpi].split(',')
                tmpi+=1
                stars1=t[0]   
                rating_counts1=info['Current Version:']
            stars2=rating_counts2=''
            if  info.has_key('All Versions:'):
                t=listname.allstart[tmpi].split(',')
                stars2=t[0]
                rating_counts2=info['All Versions:']
            description=''.join(listname.description)
            
            t=simplify(listname.whatisnew[3:])
            whats_new=''.join(t)
            iphonescreenshot=''
            for one in listname.iphonescreenshots:
                iphonescreenshot+='<screenshot type="iphone"><![CDATA[%s]]></screenshot>\n' % one
            ipadscreenshot=''
            for one in listname.ipadscreenshots:
                ipadscreenshot+='<screenshot type="ipad"><![CDATA[%s]]></screenshot>\n' % one
            usernameindex=[]
            for k in range(len(customer)):
                if re.findall(r'by\n',customer[k]):
                    usernameindex.append(k)
            review=[]
            for k in range(len(usernameindex)):
                if k!=len(usernameindex)-1:
                    t=usernameindex[k+1]-1
                else:
                    t=usernameindex[k]+2
                s='<review>\n<user><![CDATA[%s]]></user>\n<rating><![CDATA[%s]]></rating>\n<title><![CDATA[%s]]></title>\n<content><![CDATA[%s]]></content>\n</review>\n' % \
                (re.findall(r'.*$',customer[usernameindex[k]])[0].strip(),listname.customerstart[k],customer[usernameindex[k]-1],''.join(customer[usernameindex[k]+1:t]))
                review.append(s)
            review=''.join(review)#s = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f]').sub(' ', str)
            output=template % (id,name, price,category,Updated,version,size,languages,seller,copyright,app_rating,reason,requirements,\
                 stars1,rating_counts1,stars2,rating_counts2,description,whats_new,iphonescreenshot,ipadscreenshot,review)
            print '%s    %dth over!' % (threading.currentThread().getName(),i)
            output = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f]').sub(' ', output)
            print >>outputFile,output
            counts+=1
            if counts==500:
                counts=0
                print >>outputFile,'</apps>'
                outputFile.close()
                tempfilename='%s%d.xml' % (filename,i)
                outputFile=open(tempfilename,'w')
                print >>outputFile,'<apps>'
        except Exception,e:
            print str(e)
            print url
            print info
            print content
            errorqueue.put((name,url))
            print >>outputFile,'</apps>'
            outputFile.close()
            tempfilename='%s%d.xml' % (filename,i)
            outputFile=open(tempfilename,'w')
            print >>outputFile,'<apps>'
    if not counts==0:
        print >>outputFile,'</apps>' 
        outputFile.close()
   # outputFile.close()
if __name__=='__main__':
    main()
    errorfile=open('logF_starerrornameandurl.txt','w')
    tempqueue=[]
    while not errorqueue.empty():
        tempqueue.append(errorqueue.get())
    t=json.dumps(tempqueue)
    print >>errorfile,t    
    print '***********ok**********'