import urllib2
from BeautifulSoup import BeautifulSoup
import sys

url = 'http://en.wiktionary.org/wiki/' + sys.argv[1]
opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
html = opener.open(url).read()
soup = BeautifulSoup(html)

"""
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
"""
#remove the floating wikipedia image and link
for i in soup.html.body.findAll('div', {'class' : 'sister-wikipedia sister-project noprint floatright'}):
    floating = i
floating.findNext('p').extract()
floating.extract()

#extract contents only
for i in soup.html.body.findAll('div', {'id' : 'content'}):
    contents = i
soup.find(href='http://bits.wikimedia.org/skins-1.5/monobook/main.css?283l').replaceWith('<link rel="stylesheet" href="main.css" type="text/css" media="screen" />')
head = soup.html.head
tmp = '<html>' + '\n' + str(head) + '\n' + '<body>\n' + str(contents) + '\n</body>' + '</html>'
file = open('tmp.html', 'w')
file.write(tmp)
file.close()


