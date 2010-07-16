import urllib2
from BeautifulSoup import BeautifulSoup
import sys

url = 'http://en.wiktionary.org/wiki/' + sys.argv[1]
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
html = opener.open(url).read()
soup = BeautifulSoup(html)

for h3 in soup.html.body.findAll('h3'):
    if h3.findAll(id='Etymology'):
        tmp_ety = h3.findNext('p').renderContents().split('<')

etymology = ''
for i in tmp_ety:
    i = i.rstrip()
    if not i.endswith('>'):
        x = i.split('>')
        t = x[len(x) - 1]
        if t.find('&#'):
            etymology = etymology + t

print etymology

