import cookielib
import urllib
import urllib2
import xmlrpclib
import ConfigParser
from bs4 import BeautifulSoup
import csv
import re
from datetime import date
from send_mail import send_mail
import threading


__author__ = 'Carlos Espinosa'

class Spider:
    def __init__(self):
        self.opener = None
        self.RETRY_COUNT = 10
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
        try:
            urllib2.install_opener(opener)
            response = opener.open(url)
            return response.info(), response.read()
            self.REFERER = ('Referer', referer)
            if referer is not None:
                self.headers.append(self.REFERER)
            self.opener = self.createOpener(self.headers, [self.createCookieJarHandler()])
            urllib2.install_opener(self.opener)

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

class Main(threading.Thread):
    def __init__(self, url):
        self.spider = Spider()
        self.mainUrl = url
        self.referer = None

    def scrapItem(self, url,pgn=1):
        threading.Thread.__init__(self)
        tmp =url.split('/')
        urlIntern=mainUrl+'/c/buy/'+tmp[5]+'/ipp/100/ci/'+tmp[7]+'/pn/'+str(pgn)+'/N/'+tmp[9]        
        headerInfo, itemPageRequest = self.spider.fetchData(urlIntern, self.referer)
        itemPagesoup = BeautifulSoup(itemPageRequest)
        block=itemPagesoup.find_all("div", {"class": "productBlockCenter"})
        for item in block:
            itemurlinfo=item.find("div", {"id": "productTitle"})
            brand=item.find("div", {"class":"brandTop"})
            mfrinfo=item.find("li", {"class":"singleBullet"})
            importer=item.find("div", {"id": "grayMarket"}).text
            LensesNikon=True if brand.text=="Nikon" and  tmp[5]=="Lenses" else False
            if  not re.search('imported',importer, re.IGNORECASE):
                if mfrinfo!=None:            
                    mfr= mfrinfo.find("span", {"class": "value"}).text
                else:
                    mfr='' 
                itemurl=itemurlinfo.find('a')['href']
                if itemurl:
                    self.dataItems (itemurl,mfr,LensesNikon)
        if re.search('<a href="[^"]*" class="lnext">Next',itemPageRequest):
            return self.scrapItem(url, pgn + 1)

    
    def dataItems(self,url,mfr,LensesNikon):
        headerInfo, itemPageRequest = self.spider.fetchData(url, self.referer)
        dataPagesoup = BeautifulSoup(itemPageRequest)
        breadcrumbs=[]
        for li in dataPagesoup.find('ul', {'id': 'breadcrumbs'}).find_all('li'):
            breadcrumbs.append(li.text.strip())
         
        
        special_price= ''
        name=''
        code=''
        matchedStrPrice = re.search('(?i)cmCreateProductviewTag\("[^"]*?",\s*?"[^"]*?",\s*?"[^"]*?",\s*?"([^"]*)"\)', itemPageRequest)
        if matchedStrPrice:
            special_price = float(matchedStrPrice.group(1).replace('$','').replace(',',''))
        
        matchedStrCode = re.search('(?i)cmCreateProductviewTag\(\s*?"([^"]*)"', itemPageRequest)
        if matchedStrCode:
            code = matchedStrCode.group(1) 
          
        matchedStrName = re.search('(?i)cmCreateProductviewTag\("[^"]*?",\s*?"([^"]*)"', itemPageRequest)
        if matchedStrName:
            name = matchedStrName.group(1)
            
        incar="normal"
        price_rebate='0'
        date_rebate=''
                    
        print code
        info=dataPagesoup.find("div", {"id": 'productInfo'})
        if re.search('See cart for product details', info.text):
            incar="incar"

            
        if re.search('Instant Saving', info.text):
            if incar=="incar":
                incar="rebate-incar"
            else:
                incar="rebate"
            price_rebateInfo=info.find("li", {"class":"instant hiLight rebates"})
            if price_rebateInfo==None:
                log.writerow([code,'exception Rebate without value red'])
                return 0
            price_rebate=abs(float(price_rebateInfo.find("span", {"class": "value red"}).text.strip().replace('$','').replace(',','')))
             
            date_rebate=info.find("span", {"class": "offerEnds"}).text.strip()#.replace('\S', '')#.replace('\n', '').replace('\r', '')
            match=re.search(r'.......\'..',date_rebate)
            if match:
                date_rebate= match.group().replace("'",'').split()
                date_rebate[0]=monts[date_rebate[0]]
                date_rebate="20"+date_rebate[2]+"-"+date_rebate[1]+"-"+date_rebate[0]

        priceinfo=info.find("li", {"class":"price hiLight"})
        if priceinfo==None: 
            log.writerow([code,'exception any without price hilight'])
            return 0
        classaux=re.search('"*.value.*"',priceinfo.prettify())

        if classaux:
            classaux=classaux.group().replace("\"",'')
            price=float(priceinfo.find("span", {"class":classaux}).text.strip().replace('$','').replace(',',''))
            if price!= special_price and incar=="normal":
                incar=incar+"WithShow"
        
        else:
            price=special_price
            incar=incar+"WitoutShow"
 
        if mfr=='':
            parms=[{'name':str(name)}]
        else:
            parms=[{'model':str(mfr)}]
        try: 
            products = server.call(token, 'catalog_product.list',parms)
            sku=''
            for product in products:
                sku = product['sku']
        except Exception, x:
            print x
            sku=None
 
        
        if sku:
            try:
                info = server.call(token, 'catalog_product.info',[sku])
                magentoPrice= info['price']
                magentoEspecialPrice= info['special_price']
                if magentoEspecialPrice:
                    magentoEspecialPrice=float(magentoEspecialPrice)
                if magentoPrice:
                    magentoPrice=float(magentoPrice)
                if incar=="normal" and magentoPrice==price and (magentoEspecialPrice==None or magentoEspecialPrice=='' ):
                    return 0
                
                if LensesNikon:
                    special_price=price
                    incar="normal"
                
                if price!=magentoPrice or special_price!=magentoEspecialPrice or LensesNikon:

                    data=[date.today(),str(mfr),code,name,float(special_price),float(price),incar,price_rebate,date_rebate,magentoEspecialPrice,magentoPrice]
                    
                    for crumb in breadcrumbs[1:]:
                        data.append(crumb)

                    writer.writerow(data)
                    print data                       
        
        
            except Exception, x:
                print x            


if __name__ == "__main__":
    mainUrl = "http://www.bhphotovideo.com"
    monts={"JAN":"1","FEB":"2","MAR":"3","APR":"4","MAY":"5","JUN":"6","JUL":"7","AUG":"8","SEP":"9","OCT":"10","NOV":"11","DEC":"12"}
    updateArchive=str(date.today())+"_updateTotalSecondRound.csv"
    writer = csv.writer(open(updateArchive, "wb"))
    log = csv.writer(open("log.csv", "wb"))
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    tip="magento_test"
    #tip="magento_live"
    mg_url = config.get(tip, "mg_url")
    mg_username = config.get(tip, "mg_username")
    mg_password = config.get(tip, "mg_password") 
    
    server = xmlrpclib.ServerProxy(mg_url)
    token = server.login(mg_username, mg_password)
    main = Main(mainUrl)
    main.scrapItem('http://www.bhphotovideo.com/c/buy/Digital-Cameras/ci/9811/N/4288586282')
    main.scrapItem('http://www.bhphotovideo.com/c/buy/Lenses/ci/15492/N/4288584250')

    #sendMail=send_mail()
    #sendMail.send(updateArchive)


