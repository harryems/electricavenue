import ConfigParser
import cookielib
import urllib
import urllib2
from bs4 import BeautifulSoup
import csv
import re
from datetime import date



__author__ = 'Carlos Espinosa'

class Spider:
    def __init__(self):
        self.opener = None
        self.RETRY_COUNT = 5
        self.USER_AGENT = ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1')
        self.headers = [self.USER_AGENT]

    def fetchData(self, url, referer=None, parameters=None, retry=0):
        opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
                                      urllib2.HTTPHandler(debuglevel=0),
                                      urllib2.HTTPSHandler(debuglevel=0))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1')]
        cookieJar = cookielib.LWPCookieJar()
        handlers = urllib2.HTTPCookieProcessor(cookieJar)
        opener.add_handler(handlers)
        urllib2.install_opener(opener)
        response = opener.open(url)
        return response.info(), response.read()
        self.REFERER = ('Referer', referer)
        if referer is not None:
            self.headers.append(self.REFERER)
        self.opener = self.createOpener(self.headers, [self.createCookieJarHandler()])
        urllib2.install_opener(self.opener)
        try:
            if parameters is None:
                response = self.opener.open(url, timeout=30)
                return response.info(), response.read()
            else:
                response = self.opener.open(url, urllib.urlencode(parameters), timeout=30)
                return response.info(), response.read()
        except Exception, x:
            print x
            if retry < self.RETRY_COUNT:
                self.fetchData(url, referer, parameters, retry + 1)
            else:
                print 'Failed to fetch data after 5 retry.'
        return None

class Main:
    def __init__(self ):
        self.spider = Spider()
        self.referer = None

    def run(self):
        for row in infile:            
            itemUrl = (row[0])
            print itemUrl
            if re.search('bhphotovideo',itemUrl):
                paramsDescription={'class':'specWrapper bulletlist clearfix'} 
                paramsTitle={'id':'productHeadingCC'} 
#                self.bhScrapper(itemUrl)
#                break
            if re.search('calumetphoto',itemUrl):
                paramsDescription={'id':'tabs-1'}
                paramsTitle={'class':'sectionHeaderCtn'}
                #self.calumetScrapper(itemUrl)
            description,title=self.bhcalumetScrapper(itemUrl,paramsDescription,paramsTitle)
            instruction=introduction+"\n"+itemUrl+"\n"+description.text
            lineToWrite=[title,minword,maxword,quality,deadline,'1163',instruction]
            outfile.writerow(lineToWrite)
            
                
            
    def bhcalumetScrapper(self,url,paramsDescription,paramsTitle):
        description=''
        headerInfo, data = self.spider.fetchData(url)
        mainPageSoup = BeautifulSoup(data)
        descriptionSoup=mainPageSoup.find("div", paramsDescription)
        title=mainPageSoup.find("div",paramsTitle).text.strip()
        return descriptionSoup,title
        

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("configTextBroker.ini")
    minword=config.get('TextBroker', "minWords")
    maxword=config.get('TextBroker', "maxWords")
    quality=config.get('TextBroker', "quality")
    deadline=config.get('TextBroker', "deadline")

    introduction="Please follow this link (plain text in the next column) A short description about the item needs to be written, and also please rewrite the text in different fields."

    filename="lenses_links.csv"
    infile = csv.reader(open(filename))
    outfile = csv.writer(open(str(date.today())+"orderElectricAvenue.csv", "wb"))
    main = Main()
    main.run()
     

