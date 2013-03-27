import urllib
import urllib2
from bs4 import BeautifulSoup
import re
import ConfigParser
import xmlrpclib




config = ConfigParser.ConfigParser()
config.read("config.ini")
tip="magento_test"
#tip="magento_live"

#output='output.csv'
#writer = csv.writer(open("output.csv", "wb"))
mg_url = config.get(tip, "mg_url")
mg_username = config.get(tip, "mg_username")
mg_password = config.get(tip, "mg_password")

server = xmlrpclib.ServerProxy(mg_url)
token = server.login(mg_username, mg_password)
info = server.call(token, 'catalog_product.info',['013803152265'])
print info