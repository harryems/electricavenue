import xmlrpclib
import ConfigParser
import csv

class Main:
    def __init__(self):
        pass
    def insert(self):
        server = xmlrpclib.ServerProxy(mg_url)
        token = server.login(mg_username, mg_password)

        for row in infile:
            (mfr,BHcode,BHname,BHspecialprice,BHprice,typeIncar,priceRebate,dateRebate) = (row[1:9])
            if mfr=='':
                parms=[{'name':str(BHname)}]
            else:
                parms=[{'model':str(mfr)}]
            products = server.call(token, 'catalog_product.list',parms)
            sku=''
            for product in products:
                sku = product['sku']
            
            if sku:
                try:
                
                    #info = server.call(token, 'catalog_product.info',[sku])
#                    magentoPrice= info['price']
#                    magentoEspecialPrice= info['special_price']
#                    BHprice=BHprice.replace("$", '').replace(",","")
#                    priceRebate=priceRebate.replace("$", '').replace(",","")
                    data={'price':BHprice}
                    
                    if typeIncar=='normal':
                        data['msrp_enabled']='0'
                        data['msrp_display_actual_price_type']='4'
                        data['special_price']=''
                           
                    if typeIncar=='rebateWitoutShow':                     
                        data['msrp_enabled']='1'
                        data['msrp_display_actual_price_type']='1'
                        data['special_price']=BHspecialprice                    
                    if typeIncar=='incar':
                        data['msrp_enabled']='1'
                        data['msrp_display_actual_price_type']='1'
                        data['special_price']=BHspecialprice
                    if typeIncar=='rebate':
                        #data['msrp_enabled']=str(priceRebate)
                        data['special_to_date']=str(dateRebate )+' 00:00:00'
                        data['msrp_enabled']='0'
                        data['msrp_display_actual_price_type']='4'
                        data['instant_savings']=priceRebate
                        data['special_price']=BHspecialprice
                    if typeIncar=='rebate-incar':
                        data['special_to_date']=str(dateRebate )+' 00:00:00'
                        data['msrp_enabled']='1'
                        data['msrp_display_actual_price_type']='1'
                        data['instant_savings']=priceRebate
                        data['special_price']=BHspecialprice 
                        #'news_to_date': '2013-03-25 00:00:00'
                        

                    parms=[sku,data]
                    r = server.call(token, 'catalog_product.update',parms)
                    print r
                        #writer.writerow([sku])
                except Exception, x:
                    print x

        

            
            
#


if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    #tip="magento_test"
    tip="magento_live"
    filename="2013-03-27_update.csv"
    infile = csv.reader(open(filename))
    #output='output.csv'
    #writer = csv.writer(open("output.csv", "wb"))
    mg_url = config.get(tip, "mg_url")
    mg_username = config.get(tip, "mg_username")
    mg_password = config.get(tip, "mg_password")
    main = Main()
    main.insert()
