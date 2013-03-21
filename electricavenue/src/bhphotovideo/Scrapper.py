
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
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1'),
                             ('Referer', 'http://us.accessorize.com')]
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
    def __init__(self, url):
        self.spider = Spider()
        self.mainUrl = url
        self.referer = None

    def doOperation(self):
        self.scrapData(self.mainUrl, self.referer)

    def scrapData(self, url, referer):
        headerInfo, data = self.spider.fetchData(url, referer)
        mainPageSoup = BeautifulSoup(data)
        menu = mainPageSoup.find("div", {"class": "mainCategoryLinks"})
        for menuSegundoNivel in menu.find_all("a"): 
            print "Categoria"+menuSegundoNivel.get('href')
            self.scrapCategoryData( menuSegundoNivel.get('href'))

    def scrapCategoryData(self, url):
        listURL=[]
        try:
            headerInfo, categoryPageRequest = self.spider.fetchData(url, self.referer)
            categoryPagesoup = BeautifulSoup(categoryPageRequest)
            subcategoriesTipe1 = categoryPagesoup.find_all('div', {"class": "column"})
            for hrefSubCategories in subcategoriesTipe1:
                hrefsub = hrefSubCategories.find_all('a')
                for tmp in hrefsub:
                    print "\t sub categ:" + tmp.get('href')
                    self.scrapItem(tmp.get('href'))
            subcategoriesTipe2 = categoryPagesoup.find_all('div', {"class": "categoryGroup"})
            for hrefSubCategories2 in subcategoriesTipe2:
                hrefsub2 = hrefSubCategories2.find_all('a')
                for tmp2 in hrefsub2:
                    listURL.append(tmp2.get('href'))
                listURL=set(listURL)
                for tmp2 in listURL:
                    print "\t sub categ" + tmp2
                    self.scrapSubCategoryData(tmp2)

        except Exception, x:
            print x

    def scrapSubCategoryData(self, url):
        listURL=[]
        try:
            headerInfo, categoryPageRequest = self.spider.fetchData(url, self.referer)
            categoryPagesoup = BeautifulSoup(categoryPageRequest)
            subcategoriesTipe1 = categoryPagesoup.find_all('table', {"class": "catTable"})
            for hrefSubCategories in subcategoriesTipe1:
                hrefsub = hrefSubCategories.find_all('a')
                for tmp in hrefsub:
                    print " \t \t sub sub categ:" + tmp.get('href')
                    self.scrapItem(tmp.get('href'))

        except Exception, x:
            print x

    def scrapItem(self, url,pgn=1):
        tmp =url.split('/')
        urlIntern=mainUrl+'c/buy/'+tmp[5]+'/ipp/100/ci/'+tmp[7]+'/pn/'+str(pgn)+'/N/'+tmp[9]        
        headerInfo, itemPageRequest = self.spider.fetchData(urlIntern, self.referer)
        itemPagesoup = BeautifulSoup(itemPageRequest)
        block=itemPagesoup.find_all("div", {"class": "productBlockCenter"})
        for item in block:
            itemurl=item.find("div", {"id": "productTitle"})
            brand=item.find("div", {"class":"brandTop"})
            mfr=item.find("li", {"class":"singleBullet"})
            if brand.text == "Canon":
                #print brand.text
                print mfr.find("span", {"class": "value"}).text
            #self.dataItems (itemurl.find('a')['href'])
        #if re.search('<a href="[^"]*" class="lnext">Next',itemPageRequest):
        #    return self.scrapItem(url, pgn + 1)

    
    def dataItems(self,url):
        headerInfo, itemPageRequest = self.spider.fetchData(url, self.referer)
        dataPagesoup = BeautifulSoup(itemPageRequest)
        breadcrumbs=[]
        for li in dataPagesoup.find('ul', {'id': 'breadcrumbs'}).find_all('li'):
            breadcrumbs.append(li.text.strip())
         
        
        price= ''
        name=''
        code=''
        matchedStrPrice = re.search('(?i)cmCreateProductviewTag\("[^"]*?",\s*?"[^"]*?",\s*?"[^"]*?",\s*?"([^"]*)"\)', itemPageRequest)
        if matchedStrPrice:
            price = matchedStrPrice.group(1)
        
        matchedStrCode = re.search('(?i)cmCreateProductviewTag\(\s*?"([^"]*)"', itemPageRequest)
        if matchedStrCode:
            code = matchedStrCode.group(1) 
          
        matchedStrName = re.search('(?i)cmCreateProductviewTag\("[^"]*?",\s*?"([^"]*)"', itemPageRequest)
        if matchedStrName:
            name = matchedStrName.group(1) 
        price_list=dataPagesoup.find("span", {"class": "value"})
        #name=dataPagesoup.find("div", {"id": "productHeadingCC"})
        data=[date.today(),code,name,price,price_list.string]
        for crumb in breadcrumbs[1:]:
            data.append(crumb)
        writer.writerow(data)

        print code +"," +name+","+price+"," +price_list.string
if __name__ == "__main__":
    mainUrl = "http://www.bhphotovideo.com/"
    writer = csv.writer(open("camarasCanon.csv", "wb"))
    main = Main(mainUrl)
    #main.doOperation()
    main.scrapItem('http://www.bhphotovideo.com/c/buy/Lenses/ci/15492/N/4288584250')

