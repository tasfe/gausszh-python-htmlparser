#!/usr/bin/env python
#coding=utf8
#按类别收集，多线程,更完善的错误处理（网络连接错误）
#E-mail:gauss.zh@gmail.com
import urllib2
import re
import time
from sgmllib import SGMLParser

urlpat=re.compile(r'\.*itunes.apple.com/us/app.*id.*\d')
category=''
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
                match=urlpat.search(k)
                if match:
                    ret=match.group()
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
    global category
    try:
        #beginUrl=raw_input("input URL:")#http://itunes.apple.com/us/genre/ios-games/id6014?mt=8
        returnfile=urllib2.urlopen('http://itunes.apple.com/us/genre/ios-utilities/id6002?mt=8')
        content = returnfile.read()#可以设置timeout,值得单位是秒
        returnfile.close()
        listname = ListName()
        listname.feed(content)
        outputFile=open('utilitiesoutputFile.xml','w')
        print >>outputFile,'<app>'
        appname=listname.appname
        appurl=listname.appurl
        havedapp={}
        counts=0
    except Exception,e:
       print str(e)
    templatefile=open('template.xml','r')#    e.reason.errno==10054
    template=''.join(templatefile.readlines())
    templatefile.close()
    i=-1
    while True:
        i+=1
        if i>=len(appurl):
            break    
        try:
            if havedapp.has_key(appurl[i]):
                continue                        
            del(listname)
            listname=ListName()
            #appurl[i]='http://itunes.apple.com/us/app/bumbee/id434582652?mt=8'
            try:
                returnfile=urllib2.urlopen(appurl[i])
                content=returnfile.read()
                returnfile.close()
            except Exception,e:
                if e.reason.errno==10054:
                    listname=i=i-1
                    time.sleep(1)
                    continue
            havedapp[appurl[i]]=1
            listname.feed(content)
            name=re.findall(r'app/.*/id',appurl[i])[0]
            name=name[4:-3]
            appurl+=listname.appurl            
            info={}
            j=0
            tmpinfo=simplify(listname.info[0:50])
            info['price']=tmpinfo[2]    
            for one in tmpinfo:
                if one in ['Category:','Released','Updated:','Version:','Size:','Languages:','Language:',\
                           'Seller:','Requirements:','Released:','All Versions:','Current Version:']:
                    info[one]=tmpinfo[j+1]
                    if one=='Seller:':
                        info['copyright:']=tmpinfo[j+2]
                        info['app_rating:']=tmpinfo[j+3]
                        info['reasons:']=tmpinfo[j+4]
                j+=1          
            if locals().has_key('category'):
                if category!=info['Category:']:
                    continue
            else:
                category=info['Category:'] 
            id=int(re.findall(r'[\d]{5,}',appurl[i])[0])   
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
                iphonescreenshot+='<screenshot type="iphone">%s</screenshot>\n' % one
            ipadscreenshot=''
            for one in listname.ipadscreenshots:
                ipadscreenshot+='<screenshot type="ipad">%s</screenshot>\n' % one
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
                s='<review>\n<user>%s</user>\n<rating>%s</rating>\n<title>%s</title>\n<content>%s</content>\n</review>\n' % (re.findall(r'.*$',customer[usernameindex[k]])[0].strip(),listname.customerstart[k],customer[usernameindex[k]-1],''.join(customer[usernameindex[k]+1:t]))
                review.append(s)
            review=''.join(review)
            output=template %(id,name, price,category,Updated,version,size,languages,seller,copyright,\
            app_rating,reason,requirements,stars1,rating_counts1,stars2,rating_counts2,description,\
            whats_new,iphonescreenshot,ipadscreenshot,review,)
            print '%dth over!' % i
            print >>outputFile,re.sub(r'(<br>)|&','', output)
            counts+=1
            if counts==500:
                counts=0
                print >>outputFile,'</app>'
                outputFile.close()
                filename='utilitiesoutputFile%d.xml' % i
                outputFile=open(filename,'w')
                print >>outputFile,'<app>'
        except Exception,e:
            print str(e)
            print appurl[i]
    if not counts==0:
        print >>outputFile,'</app>' 
        outputFile.close()
   # outputFile.close()
if __name__=='__main__':
    main()
    print '***********ok**********'