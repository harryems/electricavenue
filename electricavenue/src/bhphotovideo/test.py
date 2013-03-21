from xmlrpclib import *
server = Server('http://www.electricavenue.net/api/xmlrpc/')
session = server.login('raymond','RayMor321')
orderlist = server.call(session, 'sales_order.list')
for x in orderlist:
    print "%s %s %s %s" % (x["increment_id"],x["billing_name"], x["status"], x["grand_total"])