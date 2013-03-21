import xmlrpclib
import ConfigParser
import csv

class Main:
    def __init__(self):
        pass
    def insert(self):
        server = xmlrpclib.ServerProxy(mg_url)
        token = server.login(mg_username, mg_password)
        infile = csv.reader(open(filename))

        for row in infile:
            (mfr,BHcode,BHname,BHspecialprice,BHprice) = (row[1:6])       
            parms=[{'model':str(mfr)}]
            products = server.call(token, 'catalog_product.list',parms)
            for product in products:
                sku = product['sku']
            
            info = server.call(token, 'catalog_product.info',[sku])
            magentoPrice= info['price']
            magentoEspecialPrice= info['special_price']
            if magentoPrice!=BHprice:
                parms=[sku,{'price':BHprice}]
                if BHspecialprice<BHprice:
                    parms.append({'special_price':BHspecialprice})
                server.call(token, 'catalog_product.update',parms)

        

            
            
#


if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    tip="magento_test"
    #tip="magento_live"
    filename="camarasCanon.csv"
    mg_url = config.get(tip, "mg_url")
    mg_username = config.get(tip, "mg_username")
    mg_password = config.get(tip, "mg_password")
    main = Main()
    main.insert()
