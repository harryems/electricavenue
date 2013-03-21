import urllib
import urllib2
import re
from bs4 import BeautifulSoup

url='http://www.bhphotovideo.com/c/buy/Lenses/ipp/100/ci/15492/pn/16/N/4288584250'
page=urllib.urlopen(url)



#soup = BeautifulSoup(page.read())
#print page
if re.search('<a href="[^"]*" class="lnext">Next', page):
    print "yes"
else:
    print "No"