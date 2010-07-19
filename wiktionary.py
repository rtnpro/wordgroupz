import urllib2
from BeautifulSoup import BeautifulSoup
import sys
import gtk
import webkit

def wikitionary_lookup(html_str):
    window = gtk.Window()
    window.set_default_size(500,600)
    window.connect("destroy", on_window_destroy)
    vbox = gtk.VBox()
    browser = webkit.WebView()
    scroller = gtk.ScrolledWindow()
    scroller.add(browser)
    vbox.pack_start(scroller)
    progress = gtk.ProgressBar()
    browser.connect("load-progress-changed", load_progress_changed)
    browser.connect("load-started", load_started)
    browser.connect("load-finished", load_finished)
    vbox.pack_start(progress, False)
    window.add(vbox)
    window.show_all()
    #browser.open('file:///home/rtnpro/webscrapping/tmp.html')
    browser.load_html_string(html_str, 'http://en.wiktionary.org/wiki/'+sys.argv[1])
    gtk.main()

def load_progress_changed(webview, amount):
    progress.set_fraction(amount/100.0)

def load_started(webview, frame):
    progress.set_visible(True)

def load_finished(webview, frame):
    progress.set_visible(False)

def on_window_destroy(widget, data = None):
    gtk.main_quit()

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
    i.findNext('p').extract()
    i.extract()

#extract contents only
for i in soup.html.body.findAll('div', {'id' : 'content'}):
    contents = i
soup.find(href='http://bits.wikimedia.org/skins-1.5/monobook/main.css?283l').replaceWith('<link rel="stylesheet" href="http://rtnpro.fedorapeople.org/main.css" type="text/css" media="screen" />')
head = soup.html.head
tmp = '<html>' + '\n' + str(head) + '\n' + '<body>\n' + str(contents) + '\n</body>' + '</html>'

file = open('tmp.html', 'w')
file.write(tmp)
file.close()


wikitionary_lookup(tmp)


