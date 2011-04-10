## Copyright (C) 2010 Ratnadeep Debnath <rtnpro@fedoraproject.org>

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
import cgi
import pygtk
import gtk
import sqlite3
import os
import sys
import socket
import string
import get_wordnet_def as wordnet
import webkit
import urllib2
from BeautifulSoup import BeautifulSoup
import urllib
import pygst
import gst
import re
from html2text import *
import get_fields
import thread
import threading
import games
import espeak
#from gettext import gettext as _
import locale
import gettext
APP = 'worgroupz'
DIR = 'locale'
VERSION = '0.3.1'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext


usr_home = os.environ['HOME']
wordgroupz_dir = usr_home+'/.wordgroupz'
audio_file_path = wordgroupz_dir + '/audio'
db_file_path = wordgroupz_dir+'/wordgroupz.db'

class wordGroupzSql:
    def db_init(self):
        if not os.path.exists(wordgroupz_dir):
            os.mkdir(wordgroupz_dir, 0755)
        conn = sqlite3.connect(db_file_path)
        c =  conn.cursor()
        tables = []
        for x in c.execute('''select name from sqlite_master'''):
            tables.append(x[0])
        if not 'word_groups' in tables:
            c.execute('''create table word_groups
            (word text, grp text, details text, wordnet text, webster text, wiktionary text, accuracy text)''')
            conn.commit()
        if not 'groups' in tables:
           c.execute('''create table groups
           (grp text, details text, wordnet text, webster text, wiktionary text)''')
           conn.commit()
        #if not 'wiktionary' in tables:
        #    c.execute('''create table wiktionary
        #   ()''')
        #alter table to port to new db format
        c.execute("""select * from groups""")
        group_cols = [i[0] for i in c.description]
        for i in ['grp', 'details', 'wordnet','webster', 'wiktionary']:
            if i not in group_cols:
                c.execute("""alter table groups add column %s text"""%(i))
                conn.commit()
                for j in self.list_groups():
                    t = (j,)
                    c.execute("""update groups set wordnet="%s" where grp=?"""%(wordnet.get_definition(j)),t)
                conn.commit()
                
        c.execute("""select * from word_groups""")
        word_groups_cols = [i[0] for i in c.description]
        #print word_groups_cols
        for i in ['wordnet', 'webster', 'wiktionary']:
            if not i in word_groups_cols:
                c.execute("""alter table word_groups add column %s text"""%(i))
                for j in self.list_words():
                    t = (j,)
                    c.execute("""update word_groups set wordnet="%s" where word=?"""%(wordnet.get_definition(j)), t)
                    conn.commit()
        if not 'accuracy' in word_groups_cols:
            c.execute("""alter table word_groups add column accuracy text""")
            c.execute("""update word_groups set accuracy='0:0'""")
            
        conn.commit()
        c.close()
        conn.close()
    def save_accuracy_for_word(self, w, val):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (w,)
        c.execute("""update word_groups set accuracy='%s' where word=?"""%(val),t)
        conn.commit()
        c.close()
    
    def list_groups(self):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        groups = []
        for row in c.execute("""select grp from groups order by grp"""):
            if row[0] is not u'':
                groups.append(row[0])
        c.close()
        return groups
    def delete_group(self, tree_value):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (tree_value,)
        c.execute("""delete from groups where grp=?""",t)
        conn.commit()
        c.close()
    def list_words_per_group(self,grp):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        words = []
        t = (grp,)
        for row in c.execute("""select word from word_groups where grp=?""",t):
            if row[0] != '':
                words.append(row[0])
        c.close()
        return words

    def list_words(self):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        words = []
        for row in c.execute("""select word from word_groups"""):
            if row[0] != '':
                words.append(row[0])
        c.close()
        return words


    def add_to_db(self,word, grp, detail):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        conn.text_factory = str
        if grp not in self.list_groups() and grp is not '':
            if word is '':
                wn = wordnet.get_definition(grp)
                t = (grp,detail,wn, '', '')
            else:
                wn = wordnet.get_definition(grp)
                t = (grp,'', wn, '', '')
            c.execute("""insert into groups values (?,?,?,?,?)""",t)
            conn.commit()
        #allow words with no groups to be added
        elif 'no-category' not in self.list_groups() and grp is '':
            c.execute("""insert into groups values ('no-category','Uncategorized words', '', '', '')""")
        if word is not '' and word not in self.list_words_per_group(grp):
            if grp == '':
                grp = 'no-category'
            wn = wordnet.get_definition(word)
            #print wn
            t = (word, grp, detail, wn, '', '', '0:0')
            c.execute('''insert into word_groups
                values(?,?,?,?,?,?,?)''', t)
            conn.commit()
        c.close()

    def get_details(self,selection):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (selection, )
        if selection in self.list_groups():
            t = (selection,)
            c.execute("""select details from groups where grp=?""",t)
            tmp = c.fetchone()[0]
            if tmp is None:
                return ''
            else:
                return tmp.strip("'")
        elif selection is None:
            return "Nothing selected"
        else:
            result = c.execute("""select word,grp,details from word_groups where word=?""",t)
            tmp = result.fetchone()
            return tmp[2]

    def update_details(self,tree_value, details):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (tree_value,)
        details = details.replace('"', "\'")
        #details = details.replace("'", "\'")
        if tree_value in self.list_groups():
            c.execute("""update groups set details="%s" where grp=?"""%(details),t)
        else:
            c.execute("""update word_groups set details="%s" where word=?"""% (details),t)
        conn.commit()
        c.close()

    def delete_word(self, tree_value):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (tree_value,)
        c.execute("""delete from word_groups where word=?""",t)
        conn.commit()
        c.close()


    def get_details_for_flashcard(self):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        c.execute("""select word, wordnet, accuracy from word_groups order by word""")
        data = c.fetchall()
        c.close()
        conn.close()
        return data

    def save_wiktionary(self, word, data):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        conn.text_factory = str
        #data = data.replace("'", "\'")
        data = data.replace('"', "'")
        #print [data]
        t = (word,)
        if word in self.list_groups():
            c.execute('''update groups set wiktionary="%s" where grp=?'''%(data), t)
        else:
            c.execute('''update word_groups set wiktionary= "%s" where word=?'''%(data), t)
        conn.commit()
        c.close()
        conn.close()

    def save_wordnet(self, word, data):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        conn.text_factory = str
        t = (word,)
        data = data.replace("'", "\'")
        data = data.replace('"', '\"')
        if word in self.list_groups():
            c.execute("""update groups set wordnet="%s" where grp=?"""%(data), t)
        else:
            c.execute("""update word_groups set wordnet="%s" where word=?"""%(data), t)
        conn.commit()
        c.close()
        conn.close()

    def save_webster(self, word, data):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        conn.text_factory = str
        data = data.replace('"', "\'")
        #data = data.replace("'", "\'")
        t = (word,)
        if word in self.list_groups():
            c.execute('''update groups set webster="%s" where grp=?'''%(data), t)
        else:
            c.execute('''update word_groups set webster="%s" where word=?'''%(data), t)
        conn.commit()
        c.close()
        conn.close()

    def get_dict_data(self, dict, word):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (word,)
        if word in self.list_groups():
            c.execute("""select %s from groups where grp=?"""%(dict), t)
        else:
            c.execute("""select %s from word_groups where word=?"""%(dict), t)
        data = c.fetchall()
        #print 'in db'
        #print data
        #print data
        c.close()
        conn.close()
        return data[0]

    def check_ws(self, word):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (word,)
        if word in self.list_groups():
            c.execute("""select webster from groups where grp=?""",t)
            data = c.fetchall()[0][0]
            if data is None or data is u'':
                status = False
            else:
                status = True
        else:
            c.execute("""select webster from word_groups where word=?""", t)
            data = c.fetchall()[0][0]
            if data is None or data is u'':
                status = False
            else:
                status = True
        c.close()
        conn.close()
        #print 'webster'
        #print [data]
        return status

    def check_wn(self, word):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (word,)
        if word in self.list_groups():
            c.execute("""select wordnet from groups where grp=?""",t)
            data = c.fetchall()[0][0]
            if data is None or data is u'':
                status = False
            else:
                status = True
        else:
            c.execute("""select wordnet from word_groups where word=?""", t)
            data = c.fetchall()[0][0]
            if data is None or data is u'':
                status = False
            else:
                status = True
        c.close()
        conn.close()
        return status

    def check_wik(self, word):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (word,)
        if word in self.list_groups():
            c.execute("""select wiktionary from groups where grp=?""",t)
            data = c.fetchall()[0][0]
            if data is None or data is u'':
                status = False
            else:
                status = True
        else:
            c.execute("""select wiktionary from word_groups where word=?""", t)
            data = c.fetchall()[0][0]
            if data is None or data is u'':
                status = False
            else:
                status = True
        c.close()
        conn.close()
        return status
        

class online_dict:
    def __init__(self, addr = 'tcp!dict.org!2628'):
        self.sock = self.dial(addr)
        self.f = self.sock.makefile("r")
        welcome = self.f.readline()
        if welcome[0:4] != '220 ':
            raise Exception("server doesn't want you (%s)" % welcome[0:4])
        r, _ = self._cmd('CLIENT python client, versionless')
        if r != '2((40))':
            raise Exception('sending client string failed')

    def dial(self, dialstr):
        proto, host, port = string.split(dialstr, '!', 2)

        if proto !='tcp':
            raise Exception('Protocols other than tcp not implemented.')
        try:
            port = int(port)
        except:
            pass
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        return sock
    def definition(self, word, db='!'):
        for key, value in [('word', word), ('database', db)]:
            if not self.validword(value):
                raise Exception('invalid %s: "%s"' % (key, value))
        r, line = self._cmd('DEFINE %s %s' % (self.quote(db), self.quote(word)))
        if r == '552':
            return []
        if r[0] in ['4', '5']:
            raise Exception('response to define: %s' % line)
        defs = []
        while 1:
            line = self._read()
            if line[0:4] == '151 ':
                _, _, db, dbdescr = self.split(line, ' ', 3)
                defs.append((db, dbdescr, '\n'.join(self._readlist())))
            else:
                break
        return defs

    def quote(self, word):
        if ' ' in word or "'" in word or '"' in word:
            return "'%s'" % string.replace(word, "'", "''")
        return word

    def split(self, line, delim, num):
        def unquote(l):
            if l[0] in ['"', "'"]:
                q = l[0]
                offset = 1
                while 1:
                    offset = string.find(l[offset:], q)
                    if offset == -1:
                        raise Exception('Invalidly quoted line from server')

                    if l[offset-1:offset+1] == (r'\%s' % q):
                        offset += 1
                    else:
                        word = string.replace(l[1:offset+1], r'\%s' % q, q)
                        l = string.lstrip(l[offset+2:])
                        break
            else:
                word, l = string.split(l, delim, 1)
            return word, l

        r = []
        l = line
        while num != 0:
            word, l = unquote(l)
            r.append(word)
            num -= 1
        word, rest = unquote(l)
        r.append(word)

        return r

    def validword(self, s):
        bad = [chr(i) for i in range(20)]
        if s == '':
            return 0
        for c in s:
            if c in bad:
                return 0
        return 1

    def _cmd(self, cmd):
        self.sock.sendall(cmd + '\r\n')
        self.f.flush()
        line = self._read()
        code = line[0:3]
        return code, line

    def _read(self):
        line = self.f.readline()
        if line[-1] == '\n':
            line = line[0:-1]
        if line[-1] == '\r':
            line == line[0:-1]
        return line

    def _readlist(self):
        lines = []
        while 1:
            line = self._read()
            if line.startswith('.'):
                break
            if line[0:2] == '..':
                line = line[1:]
            lines.append(line)
        return lines

    def match(self, word, db='!', strat='.'):
        for key, value in [('word', word), ('database', db), ('strategy', strat)]:
            if not self.validword(value):
                raise Exception('invalid %s: "%s"' % (key, value))
        r, line = self._cmd('MATCH %s %s %s' % (self.quote(db), self.quote(strat), self.quote(word)))
        if r == '552':
            return []
        if r[0] in ['4', '5']:
            raise Exception('response to match: %s' % line)
        lines = [tuple(self.split(l, ' ', 1)) for l in self._readlist()]
        line = self._read()
        if line[0:4] != '2((40)) ':
            raise Exception('expected code 2((40)) after match (%s)' % line)
        return lines
    
    def get_def(self, word):
        l = self.match(word, db='!', strat='exact')
        for db, word in l:
            defs = self.definition(word, db=db)
            if defs == []:
                #print >> sys.stderr, 'no-match'
                return 2
            db, dbdescr, defstr = defs[0]
            s = '\n\n\n'.join([defstr for _, _, defstr in defs])
        #print s
        return s

class WebView(webkit.WebView):
    def get_html(self):
        self.execute_script('oldtitle=document.title;document.title=document.documentElement.innerHTML;')
        html = self.get_main_frame().get_title()
        self.execute_script('document.title=oldtitle')
        return html


class get_wiki_data:
    def __init__(self, filename):
        self.f = open(filename, 'r')
        self.s = self.f.read()
        self.sections = self.s.split('\n## ')
        self.pos = ['Noun', 'Verb', 'Pronoun', 'Adjective', 'Adverb', 'Preposition', 'Conjunction', 'Interjection', 'Antonyms', 'Synonyms']

    def get_contents(self):
        for i in self.sections:
            if i.split('\n')[0].endswith('Contents'):
                self.contents = i
        #print self.contents

    def get_eng_fields(self):
        self.fields = []
        self.subfields = []
        l = self.contents.split('\n  *')
        for i in l:
            i = i.split('\n')
            #print i[0]
            #print i[0].find('English')

            if i[0].find('English') > 0:
                for j in i:
                    '''
                    if j.startswith('    *'):
                        j = j.strip('    * ')
                        j = j[5: j.find(']')]
                        self.fields.append([j])
                    '''
                    j = j.strip()
                    j = j.lstrip('* [')
                    j = j.split('][')[0]
                    j = j.split(' ', 1)
                    index = j[0].split('.')
                    if index[0] == '1':
                        self.fields.append(j)

        #print self.fields

    def cleanup(self):
        #for i in self.fields:
        for key in self.dict.keys():
            #print self.dict[key]
            for i in self.dict[key]:
                links = re.findall('\[.*?\]', i)
                for link in links:
                    index = self.dict[key].index(i)
                    if link.strip('[').strip(']').isdigit():
                        i = i.replace(link, '')
                    else:
                        i = i.replace(link, link.strip('[').strip(']'))
                    i = i.strip('\n ')
                    self.dict[key][index] = i
            #print self.dict[key]

    def show(self, key):
        if key in self.dict.keys():
            #print key+':'
            count = 1
            for i in self.dict[key]:
                #print '\t'+ str(count)+'. '+i
                count = count + 1
    def get_field_details(self):
        self.dict = {}

        for i in self.sections:
            if i.split('\n')[0].endswith('English'):
                self.eng_sec = i
        #print self.eng_sec
        self.eng_secs = self.eng_sec.split('\n###')
        count = 0
        for i in self.eng_secs:
            #count = 0
            #self.dict[' '.join(self.fields[count])] = i
            #count = count + 19
            '''
            i = i.split('[')
            #print i[3]+'^s'
            for j in i:
                if j.find(']')>=0:
                    t = j.find(']')
                    sub = j[0:t+1]
                    if sub.rstrip(']').isdigit():
                        new = j[t+1:-1]
                    else:
                        new = j[0:t] + j[t+1:-1]
                    index = i.index(j)
                    #i.remove(j)
                    #i.insert(index, new)
                    i[index]=new
                 else:
                     index=i.index(j)
                     i[index]=j
            i =  ''.join(i)'''
            #print i
            '''print i
            links = re.findall('\[.*?\]', i)
            #print links
            for link in links:
                if link.strip('[').strip(']').isdigit:
                    i = i.replace(link, '')
                else:
                    i = i.replace(link, link.strip('[').strip(']'))
                    #print i'''

            t = i.split('\n')
            if t[0].find('Etymology')>= 0:
                #print '^i\n'+i
                if 'Etymology' not in self.dict.keys():
                    self.dict['Etymology'] = ['\n'.join(t[1:-1])]
                else:
                    self.dict['Etymology'].append('\n'.join(t[1:-1]))
            elif t[0].find('Pronunciation')>=0:
                if 'Pronunciation' not in self.dict.keys():
                    self.dict['Pronunciation'] = ['\n'.join(t[1:-1])]
                else:
                    self.dict['Pronunciation'].append('\n'.join(t[1:-1]))
            elif t[0].split(']')[-1] in self.pos:
                title = t[0].split(']')[-1]
                if title not in self.dict.keys():
                    self.dict[title] = ['\n'.join(t[1:-1])]
                else:
                    self.dict[title].append('\n'.join(t[1:-1]))

        self.cleanup()
        self.show('Etymology')
        #print self.dict.keys()




class wordzGui:
    wordz_db=wordGroupzSql()
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("wordgroupz.glade")
        self.window = self.builder.get_object("MainWindow")
        self.window.set_icon_from_file("/usr/share/pixmaps/wordgroupz.png")
        self.window.set_title(_("wordGroupz"))
        self.builder.connect_signals(self)
        self.get_word = self.builder.get_object("get_word")
        self.get_group = gtk.combo_box_entry_new_text()
        self.get_group.set_tooltip_text("Enter a group for your word")
        self.details = self.builder.get_object("textview1")
        self.eventbox1 = self.builder.get_object('eventbox1')
        
        self.eventbox2 = self.builder.get_object('eventbox2')
        self.eventbox2.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#444444'))
        self.eventbox1.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        self.get_group_new = gtk.combo_box_entry_new_text()
        self.get_group_new.set_tooltip_text("Enter a group for your word")
        
        self.eventbox1.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#444444'))
        self.get_group.child.connect('key-press-event',self.item_list_changed)
        self.frame2 = self.builder.get_object('frame2')
        self.frame2.hide()
        
        self.preview_button = self.builder.get_object("preview_button")
        self.preview_entry = self.builder.get_object("preview_entry")
        self.preview_button.connect("clicked",self.on_preview_button_clicked)
        #self.preview_word = self.preview_entry.get_text()
        
        
        #self.vpan = self.builder.get_object("vpaned1")
        self.output_txtview = self.builder.get_object("textview2")
        for x in wordz_db.list_groups():
            self.get_group.append_text(x)
            self.get_group_new.append_text(x)
            
        self.table1 = self.builder.get_object("table1")
        self.table2 = self.builder.get_object("table2")
        
        self.get_group.show()
        self.get_group_new.show()
        
        self.table1.attach(self.get_group, 1,2,1,2)
        self.table2.attach(self.get_group_new,0,1,0,1)

        self.hbox5 = self.builder.get_object("hbox5")
        self.hbox5.hide()
        self.treestore = gtk.TreeStore(str, int)
        self.new_word = []
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        c.execute("""select word, accuracy from word_groups""")
        self.ls = []
        self.ls = c.fetchall()
        #print 'l', self.ls
        c.close()
        self.acc_dict = {}
        for i in self.ls:
            if i[1] == u'0:0':
                self.acc_dict[i[0]] = 0
            else:
                t = i[1].split(':')
                acc = float(t[0])/float(t[1])*100
                acc = int(acc)
                self.acc_dict[i[0]] = acc
        #print self.acc_dict.keys()
        for group in wordz_db.list_groups():
            l = wordz_db.list_words_per_group(group)
            t = 0
            count = 0
            for i in l:
                if i not in self.new_word:
                    t = t + self.acc_dict[i]
                    count = count + 1
            if count != 0:
                t = t/count
            else:
                t = 0
            piter = self.treestore.append(None, [group,t])

            #self.cellpb.hide()
            for word in wordz_db.list_words_per_group(group):
                self.treestore.append(piter, [word,self.acc_dict[word]])
                #self.cellpb.set_property('text', None)
                if self.acc_dict[word] == 0:
                    #self.cellpb.set_property('text', 'New')
                    pass
                """
                try:
                    self.treestore.append(piter, [word,self.acc_dict[word]])
                except:
                    self.treestore.append(piter, [word,'n/a'])"""

        self.treeview = gtk.TreeView()
        self.tvcolumn = gtk.TreeViewColumn(_('Word Groups'))
        self.tvcolumn1 = gtk.TreeViewColumn(_('Accuracy'))
        self.treeview.append_column(self.tvcolumn)
        self.treeview.append_column(self.tvcolumn1)
        #self.treeview.append_column(self.tvcolumn1)
        self.cell = gtk.CellRendererText()
        self.cellpb = gtk.CellRendererProgress()
        #self.cell1 = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.tvcolumn1.pack_start(self.cellpb, True)
        #self.tvcolumn.pack_start(self.cell1, True)
        self.tvcolumn1.add_attribute(self.cellpb, 'value', 1)
        self.cellpb.set_property('text', None)
        self.tvcolumn1.set_cell_data_func(self.cellpb, self.custom_tree_col_view, None)
        
        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.treeview.set_reorderable(False)
        #self.tvcolumn1.pack_start(self.cell1, True)
        #self.tvcolumn1.add_attribute(self.cell1, 'active', 1 )
        self.selection = self.treeview.get_selection()
        self.selection.connect('changed', self.tree_select_changed)
        self.treeview.set_tooltip_text("Shows words classified in groups")
        self.treeview.set_model(self.treestore)
        self.treeview.show()
        self.treeview.expand_all()
        
        #self.scrolledwindow2 = self.builder.get_object("scrolledwindow2")
        #self.scrolledwindow2.add_with_viewport(self.treeview)
        self.scrolledwindow2 = gtk.ScrolledWindow()
        self.scrolledwindow2.add(self.treeview)
        self.scrolledwindow2.show()
        #print self.scrolledwindow2.get_policy()
        self.scrolledwindow2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.vbox6 = self.builder.get_object('vbox6')
        self.vbox6.pack_start(self.scrolledwindow2)
        
        self.search=self.builder.get_object("search")
        #self.search.connect('changed',self.on_search_changed)
        
        self.chose_dict_hbox = self.builder.get_object('hbox7')
        vseparator = gtk.VSeparator()
        vseparator.show()
        """
        self.chose_dict = gtk.combo_box_new_text()
        for dict in ['webster', 'wordnet', 'wiktionary']:
            self.chose_dict.append_text(dict)
        self.chose_dict.set_active(1)
        self.chose_dict.show()
        self.hbox5.pack_start(self.chose_dict, False, True, padding = 5)"""
        
        #webkit in scrolledwindow4
        self.web_vbox = self.builder.get_object('vbox14')
        #self.scroller = gtk.ScrolledWindow()
        #self.scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.browser = WebView()
        #self.browser.settings.enable_universal_access_from_file_uris(True)
        self.settings = self.browser.get_settings()
        #self.settings.set_property("enable-file-access-from-file-uris", True)
        self.settings.set_property('enable-page-cache', True)
        self.settings.set_property('user-stylesheet-uri', 'http://rtnpro.fedorapeople.org/main.css')
        self.settings.set_property('enable-universal-access-from-file-uris', True)
        self.browser.set_settings(self.settings)
        #self.browser.show()
        #self.scroller.add(self.browser)
        #self.web_vbox.pack_start(self.scroller)
        #self.scroller.show()
        self.progress = gtk.ProgressBar()
        self.progress.hide()
        self.browser.connect("load-progress-changed", self.load_progress_changed)
        self.browser.connect("load_started", self.load_started)
        self.browser.connect("load-finished", self.load_finished)
        #self.browser.connect('navigation-requested', self._navigation_requested_cb)
        self.web_vbox.pack_start(self.progress, False)
        
        #self.vbox9 = self.builder.get_object('vbox9')
        #self.vbox9.pack_start(self.web_vbox)
        #self.web_vbox.show()
        #self.vbox9.show()
        #self.status_label = self.builder.get_object('label9')
        #self.status_label.hide()
        #self.save_audio = self.builder.get_object('save_audio')
        #self.save_audio.set_label('Download pronunciation')
        self.vbox7 = self.builder.get_object('vbox7')
        self.hbox2 = self.builder.get_object('hbox2')
        self.welcome = self.builder.get_object('frame3')
        self.frame4 = self.builder.get_object('frame4')
        
        self.frame2.hide()
        self.frame4.hide()
        #self.hbox2.pack_start(self.welcome)
        self.welcome.show()
        self.note = self.builder.get_object('label16')
        self.note.set_markup('<span foreground="white"><big><big><big><b>Welcome to wordGroupz</b></big></big></big></span>')
        self.note.set_alignment(0.5, 0.2)
        '''
        self.toolbar = self.builder.get_object('toolbar1')
        self.speak_icon = gtk.Image()
        self.speak_icon.set_from_stock(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.speak_button = self.toolbar.append_item(
            '',
            'Speak',
            'Private',
            self.speak_icon,
            self.on_speak_clicked
            )
        self.toolbar.append_space()
        #tool_item = self.toolbar.get_nth_item(1)
        #tool_item.set_expand(False)'''
        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        #wiktionary
        self.wiki_word = ''
        self.browser_load_status = ''

        #Menubar
        
        '''self.file_item = gtk.MenuItem('_File')
        self.dict_item = gtk.MenuItem('_Dictionary')
        self.help_item = gtk.MenuItem('_Help')'''
        self.menubar = self.builder.get_object('menubar1')
        self.game_item = gtk.MenuItem('_Games')
        self.game_item.show()
        self.game_item_sub = gtk.Menu()
        self.flash_card = gtk.MenuItem('_Flash Card')
        self.mcq = gtk.MenuItem('_MCQ')
        self.game_item_sub.append(self.flash_card)
        self.game_item_sub.append(self.mcq)
        self.game_item_sub.show_all()
        self.menubar.insert(self.game_item, 1)
        self.file_item = self.builder.get_object('file_item')
        self.help_item = self.builder.get_object('help_item')
        self.file_item_sub = gtk.Menu()
        self.quit = gtk.MenuItem('_Quit')
        self.file_item_sub.append(self.quit)
        self.quit.show()
        self.help_item_sub = gtk.Menu()
        self.about = gtk.MenuItem('_About')
        self.about.show()
        self.help_item_sub.append(self.about)
        self.game_item.set_submenu(self.game_item_sub)
        self.file_item.set_submenu(self.file_item_sub)
        self.help_item.set_submenu(self.help_item_sub)

        self.flash_card.connect('activate', self.on_flash_card_clicked)
        self.mcq.connect('activate', self.on_mcq_clicked)
        self.about.connect('activate', self.on_about_clicked)
        self.quit.connect('activate', self.on_MainWindow_destroy)

        self.selected_word = self.builder.get_object('word_sel')
        self.selected_word.hide()
        self.audio_found = False

        #details treeview
        self.details_treestore = gtk.TreeStore(str)
        self.details_treeview = gtk.TreeView(self.details_treestore)
        
        
        self.details_cell = gtk.CellRendererText()
        self.details_tvcolumn = gtk.TreeViewColumn(_('Details'),self.details_cell,markup=0)
        self.details_treeview.append_column(self.details_tvcolumn)
        #self.details_tvcolumn.pack_start(self.details_cell, True)
        self.details_tvcolumn.add_attribute(self.details_cell, 'text', 0)
        self.details_treeview.set_search_column(0)
        self.details_tvcolumn.set_sort_column_id(0)
        self.details_treeview.set_reorderable(False)
        self.details_treeview.show_all()
        self.details_treeview.expand_all()
        self.scroller3 = self.builder.get_object('scrolledwindow3')
        #self.scroller3.add(self.details_treeview)
        #self.scroller3.show()
        self.vbox12 = self.builder.get_object('vbox12')
        self.vbox8 = self.builder.get_object('vbox8')
        self.vbox13 = self.builder.get_object('vbox13')
        #self.vbox12.set_spacing(10)
        self.delete_b = self.builder.get_object('delete')
        self.play_b = self.builder.get_object('speak')

    def custom_tree_col_view(self, column, renderer, model, iter, data):
        word = model.get_value(iter, 0)
        for i in self.ls:
            if i[0] == word and i[1] == '0:0' and word not in self.new_word:
                #print i
                self.new_word.append(word)
                #print self.new_word
            elif i[0]==word and i[1]!='0:0':
                try:
                    self.new_word.remove(word)
                except:
                    pass
        #print self.new_word
        if  word in self.new_word:
            renderer.set_property('text', 'New')
        else:
            renderer.set_property('text', None)

    
    def on_preview_button_clicked(self, widget=None, event=None):
	self.get_word = self.preview_entry.get_text()
	#self.clear_preview_word()
	self.show_meaning()
	
    #def clear_preview_word(self, widget=None, event=None):
	#label = gtk.Label()
	#print 'test'
	##label.set_text(' ')
	#table = self.builder.get_object('table3')
	#table.attach(label,0,1,0,1)
	#txt = ' '
	#label.set_markup('<span foreground="white"><b>%s</b></span>'%txt)
	#label.show()
	
    def show_meaning(self,widget=None, event=None):
	self.frame2.hide()
	self.welcome.hide()
        #self.frame4.show()
        table = self.builder.get_object('table3')
        #preview_view_word = gtk.Label()
        
        preview_view_word = self.builder.get_object('label13')
        #event = gtk.EventBox()
        #preview_view_word.set_has_tooltip(True)
        preview_view_word.set_text(self.get_word)
        #table.attach(preview_view_word,0,1,0,1)
        #preview_view_word.set_markup('<span foreground="white"><b>%s</b></span>'%self.get_word)
	#event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#AED6EF'))
        preview_view_word.show()
        #preview_view_word.set_text(' ')
        #event.show()
        
        scrolledwindow5 = self.builder.get_object('scrolledwindow5')
        preview_label = self.builder.get_object('preview_label')
	preview_event = self.builder.get_object('eventbox3')
	temp = wordnet.get_definition(self.get_word)
	#scrolledwindow5.add(preview_event)
	preview_event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#AED6EF'))
	preview_label.set_line_wrap(True)
	preview_label.set_selectable(True)
	preview_label.set_text(temp)
	self.frame4.show()
	
    def on_flash_card_clicked(self, widget=None, event=None):
        self.window.hide()
        game = games.flash()
        #game.g.builder.get_object('window2').show()
        self.window.show()
        
    def on_preview_add_clicked(self, widget, data=None):
	word = self.preview_entry.get_text()
        self.new_word = []
        if word not in self.new_word and word not in wordz_db.list_words():
            self.new_word.append(word)

        get_group_ch = self.get_group_new.child
        group = get_group_ch.get_text()
        conts = self.details.get_buffer()
        start = conts.get_iter_at_offset(0)
        end = conts.get_iter_at_offset(-1)
        detail = conts.get_text(start, end)
        wordz_db.add_to_db(word, group, detail)
        self.refresh_groups(group)
        self.treestore.clear()
        #print self.new_word
        self.on_back_clicked()
        
    def on_mcq_clicked(self, widget=None, event=None):
        self.window.hide()
        game = games.mcq()
        self.treestore.clear()
        self.new_word = []
        self.on_back_clicked()
        self.window.show()
        '''
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        c.execute("""select word, accuracy from word_groups""")
        self.ls = c.fetchall()
        #print 'l', l
        c.close()
        self.new_word = []
        self.acc_dict = {}
        for i in self.ls:
            if i[1] == u'0:0':
                self.acc_dict[i[0]] = 0
            else:
                t = i[1].split(':')
                acc = float(t[0])/float(t[1])*100
                acc = int(acc)
                self.acc_dict[i[0]] = acc
        #print self.acc_dict
        for group in wordz_db.list_groups():
            l = wordz_db.list_words_per_group(group)
            t = 0
            count = 0
            for i in l:
                if i not in self.new_word:
                    t = t + self.acc_dict[i]
                    count = count + 1
            if count!=0:
                t = t/count
            else:
                t = 0
            #print self.acc_dict.keys()
            piter = self.treestore.append(None, [group,t])
            for word in wordz_db.list_words_per_group(group):
                self.treestore.append(piter, [word,self.acc_dict[word]])
        self.treeview.expand_all()
        self.window.show()'''
    def on_speak_clicked(self, widget=None, event=None):
        filepath = audio_file_path+'/'+self.tree_value+'.ogg'
        #print filepath
        if os.path.isfile(filepath):
            self.player.set_property("uri", "file://" + filepath)
            self.player.set_state(gst.STATE_PLAYING)
        else:
            self.player.set_state(gst.STATE_NULL)
            word = self.tree_value
            espeak_obj = espeak.espeak()
            espeak_obj.speak(word)

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            #print "Error: %s" % err, debug


    def hello(self,widget=None, event=None):
        #print 'hello'
        pass
        
    def look_for_audio(self):
        page = self.browser.get_html()
        #print page
        soup = BeautifulSoup('<html>'+str(page)+'</html>')
        div = soup.html.body.findAll('div', attrs={'id':'ogg_player_1'})
        if div is None:
            #print "No audio available"
            pass
            
        else:    
            l = str(div).split(',')
            for i in l:
                if i.find('videoUrl')>0:
                    self.download_url = i.split(': ')[1].strip('"')
                    #print self.download_url
                    self.wiki_word = str(soup.html.title).split(' ')[0].split('>')[1]
                    #print "wiki_word" + self.wiki_word
                    self.save_audio.set_sensitive(True)
                    self.audio_file = self.wiki_word+'.ogg'
                    #print self.audio_file
    def on_save_audio_clicked(self, widget=None, event=None):
        '''
        network_req = webkit.NetworkRequest(self.download_url)
        #network_req.set_uri(self.download_url)
        download = webkit.Download()
        download.set_destination_uri('./')
        download.start()'''
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        audio = opener.open(self.download_url).read()
        if not os.path.exists(audio_file_path):
            os.mkdir(audio_file_path, 0755)
        file = open(audio_file_path+'/'+self.audio_file, 'wb')
        file.write(audio)
        file.close()
        
        
    """    
    def _navigation_requested_cb(self, view, frame, networkRequest):
        uri = networkRequest.get_uri()
        if uri == self.url:
            #print "request to go to %s" % uri
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            page = opener.open(uri).read()
            
            #print page.read()
            soup = BeautifulSoup(page)
            
            #extract contents
            for i in soup.html.body.findAll('div', {'id' : 'content'}):
                contents = i
            #print contents
            soup.find(href='http://bits.wikimedia.org/skins-1.5/monobook/main.css?283l').replaceWith('<link rel="stylesheet" href="http://rtnpro.fedorapeople.org/main.css" type="text/css" media="screen" />')
            head = soup.html.head
            tmp = '<html>' + '\n' + str(head) + '\n' + '<body>\n' + str(contents) + '\n</body>' + '</html>'
            view.load_string(tmp, "text/html", "utf-8", uri)
        
        
        return 1
    """
    
    def load_progress_changed(self, webview, amount):
        self.progress.set_fraction(amount/100.0)
        self.browser_load_status='loading'

    def load_started(self, webview, frame):
        self.progress.set_visible(True)
        self.browser_load_status='started'

    def load_finished(self, webview, frame):
        self.progress.set_visible(False)  
        self.browser_load_status = 'finished'
        if self.count == 0:
            self.count = 1
        else:
            self.look_for_audio()
            return
        html = self.browser.get_html()
        self.head_file = open('wiktionary_header', 'r')
        self.head = self.head_file.read()
        self.head_file.close()
        self.head = self.head.replace('enter_title', self.tree_value)
        #self.status_label.set_text('Scrapping...')
        soup = BeautifulSoup(self.head+'<body>'+html+'</body></html>')

        #extract contents
        div = soup.findAll('div', attrs={'id':'ogg_player_1'})
        #print div
        self.wiki_word = str(soup.html.title).split(' ')[0].split('>')[1]
        if div is None:
            #print "No audio available"
            self.word_audio_found = False
        else:
            #print 'hi'
            l = str(div).split(',')
            for i in l:
                if i.find('videoUrl')>0:
                    self.download_url = i.split(': ')[1].strip('"')
                    #print self.download_url
                    self.wiki_word = str(soup.html.title).split(' ')[0].split('>')[1]
                    #print 'wiki_word'+self.wiki_word
                    #self.save_audio.set_sensitive(True)
                    self.audio_file = self.tree_value+'.ogg'
                    self.audio_found = True
                    self.on_save_audio_clicked()
                    #print self.audio_file
                    
        self.audio_checked = True
        #for i in soup.html.body.findAll('div', {'id' : 'content'}):
        #    contents = i
        #soup.find(href='http://bits.wikimedia.org/skins-1.5/monobook/main.css?283n').replaceWith('<link rel="stylesheet" href="http://rtnpro.fedorapeople.org/main.css" type="text/css" media="screen" />')
        for i in soup.findAll('table', attrs={'class' : 'audiotable'}):
            i.extract()
        tmp =  str(soup)
        self.tmp = tmp
        self.browser.load_string(tmp, "text/html", "utf-8", self.url)
        txt_html = html2text(tmp, self.url)
        wiki_txt = get_fields.main(txt_html)
        wordz_db.save_wiktionary(self.tree_value, wiki_txt)
        self.show_details_tree() 

        
    def on_lookup_wiki_clicked(self, widget=None,event=None):
        self.count = 0
        url = 'http://en.wiktionary.org/wiki/' + self.tree_value + '?action=render'
        self.url = url
        #html = urllib.urlopen(self.url).read()
        #soup = BeautifulSoup(html)
        #opener = urllib2.build_opener()
        #opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        #html = opener.open(url).read()
        #file = open('tmp.html', 'w')
        #file.write(tmp)
        #file.close()
        #change jul 27
        #self.scroller.remove(self.browser)
        #self.browser.open(url)
        #self.browser.hide()
        self.browser.open(self.url)
        self.browser.hide()

    def on_backward_clicked(self, widget):
        #print 'back clicked'
        #print self.browser.get_back_forward_list().get_back_list()
        """if not self.browser.can_go_back():
            self.browser.load_string(self.tmp, "text/html", "iso-8859-15", self.url)"""
        self.browser.go_back()
        #    self.browser.load_html_string(self.tmp, self.url)

    def on_forward_clicked(self, widget):
        self.browser.go_forward()

    """
    def on_notebook1_change_current_page(self, widget=None, event=None):
        notebook1 = self.builder.get_object('notebook1')
        #print notebook1.get_current_page()"""
    
    def on_notebook1_switch_page(self, notebook, page, page_num):
        #print 'page switched'
        #print page_num
        #width, height = self.window.get_size()
        """
        if page_num==1:
            #self.window.resize(max(width, 800), max(height, 5((40))))
            #print self.tree_value, self.wiki_word, self.browser_load_status
            '''
            if self.tree_value == self.wiki_word and (self.browser_load_status is 'finished' or 'loading'):
                pass
            else:
                #self.url = 'http://en.wiktionary.org/wiki/' + self.tree_value
                #self.browser.open(self.url)
                #self.on_lookup_wiki_clicked()'''
        elif page_num == 0:
            self.show_details_tree()"""
        #self.show_details_tree()
        #self.show_details_tree()
        if page_num == 0:
            self.show_details_tree()
        elif page_num == 1:
            self.show_details_tree()
        elif page_num == 2:
            self.show_details_tree()
    def on_notebook2_switch_page(self, notebook, page, page_num):
        if page_num == 0:
            self.show_details_tree()
        elif page_num == 1:
            if self.tree_value == self.wiki_word and (self.browser_load_status is 'finished' or 'loading'):
                pass
            else:
                self.on_lookup_wiki_clicked(self.tree_value)
            
            
    def on_search_changed(self,widget=None,event=None):
        search_txt = self.search.get_text()
        words = list
        self.treestore.clear()
        if search_txt == '':
            self.on_back_clicked()
            return
        for group in wordz_db.list_groups():
            for i in wordz_db.list_words_per_group(group):
                if i.startswith(search_txt):
                    piter = self.treestore.append(None, [i, self.acc_dict[i]])
                
                    #for word in wordz_db.list_words_per_group(group):
                    #    self.treestore.append(piter, [word])

    def tree_select_changed(self, widget=None, event=None):
        self.model, self.iter = self.selection.get_selected()
        self.frame2.show()
        if self.iter is not None:
            self.delete_b.set_sensitive(True)
            self.play_b.set_sensitive(True)
            if self.welcome is self.hbox2.get_children()[1]:
                self.welcome.hide()
                self.frame4.hide()
                
            #    self.hbox2.remove(self.welcome)
            #    self.hbox2.pack_start(self.builder.get_object('frame2'))
            self.tree_value = self.model.get_value(self.iter,0)
            #print self.tree_value
            self.selected_word.show()
            self.selected_word.set_text(self.tree_value)
            #self.notebook2 = self.builder.get_object('notebook2')
            #cur_page = self.notebook2.get_current_page()
            #if self.tree_value not in wordz_db.list_groups():
            #print self.tree_value
            self.hbox5.show()
            '''
                w, h = self.window.get_size()
                self.vpan.set_position(h)
                tmp = self.vpan.get_position()
                self.vpan.set_position(int((240.0/4((40)))*h))
            else:
                self.vpan.set_position(10000)
                self.hbox3.hide()'''
            
            #if self.output_txtview.get_editable():
            #    self.output_txtview.set_editable(False)
            detail = wordz_db.get_details(self.tree_value)
            buff = self.output_txtview.get_buffer()
            buff.set_text(detail)
            self.output_txtview.set_buffer(buff)
            #self.output_txtview.modify_font(self.fontdesc)
            self.show_details_tree()

    def show_details_tree(self):
        self.details_treestore.clear()
        wn = ''
        wik = ''
        ws = ''
        self.welcome.hide()
        self.frame4.hide()
        for i in self.vbox12.get_children():
            self.vbox12.remove(i)
        for i in self.vbox8.get_children():
            self.vbox8.remove(i)
        for i in self.vbox13.get_children():
            self.vbox13.remove(i)
        try:
            wn = wordz_db.get_dict_data('wordnet', self.tree_value)[0]
        except:
            pass
        try:
            ws = wordz_db.get_dict_data('webster', self.tree_value)[0]
        except:
            pass
        try:
            wik = wordz_db.get_dict_data('wiktionary', self.tree_value)[0].strip("'")
            #print "wiktionary"+ wik
        except:
            pass
        
        try:
            if wn != u'':
                table = gtk.Table(columns=2)
                table.show()
                self.vbox12.pack_start(table, False, padding = 5)
                i = 0
                t = wn.split('\n')
                #piter = self.details_treestore.append(None, ['<span foreground="blue"><big><b>Wordnet</b></big></span>'])
                for x in t:
                    if not x.startswith('\t') and x is not u'':
                        #sub_iter = self.details_treestore.append(piter, ['<b>'+x+'</b>'])
                        #hbox_n = gtk.HBox()
                        event_b = gtk.EventBox()
                        event_b.set_visible_window(True)
                        event_b.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#AED6EF"))
                        frame = gtk.Frame()
                        frame.set_shadow_type(gtk.SHADOW_OUT)
                        #frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("grey"))
                        
                        frame.show()
                        event_b.show()
                        #hbox_n.pack_start(frame, false)
                        #hbox_n.show_all()
                        label = gtk.Label(x)
                        label.set_alignment(0.0, 0)
                        #hbox_n.pack_start(label, False, padding = 2)
                        table.attach(label, 0, 1, i, i+1, xoptions = gtk.FILL)
                        label.show()
                        #hbox_n.pack_start(frame, padding = 10)
                        table.attach(frame, 1, 2, i, i+1)
                        table.set_row_spacing(i, 10)
                        table.set_col_spacing(0, 5)
                        #hbox_n.show()
                        #self.vbox12.pack_start(hbox_n, False, padding=5)
                        vbox = gtk.VBox()
                        vbox.show_all()
                        event_b.add(vbox)
                        frame.add(event_b)
                        i = i + 1
                    elif x.startswith('\t') and not x.startswith('\tSynonyms:'):
                        #sub_sub_iter = self.details_treestore.append(sub_iter, [x.strip('\t')])
                        vbox1 = gtk.VBox()
                        label = gtk.Label()
                        label.set_line_wrap(True)
                        l = len(x.strip('\t'))
                        label.set_markup('<b><big>'+x.strip('\t')[0:2]+'</big></b>'+x.strip('\t')[2:l])
                        #label.set_markup(x.strip('\t'))
                        ##print x.lstrip('\t')[0:2]
                        #l = len(x.strip('\t'))
                        #print x.lstrip('\t')[0:l]
                        if self.window.get_size() == self.window.get_default_size():
                            label.set_width_chars(40)
                            label.set_line_wrap(True)
                        label.set_selectable(True)
                        label.set_alignment(0.0, 0.5)
                        label.show()
                        #label.show()
                        vbox1.pack_start(label, True)
                        vbox1.show()
                        vbox.pack_start(vbox1, False)
                        
                    elif x.startswith('\tSynonyms:'):
                        #self.details_treestore.append(sub_sub_iter, [x.strip('\t').replace('Synonyms', '<span foreground="blue">Synonyms</span>')])
                        frame = gtk.Frame(_('Synonyms'))
                        label = gtk.Label()
                        label.set_width_chars(40)
                        label.set_line_wrap(True)
                        label.set_markup(('<b><span foreground="white">'+ cgi.escape(x.strip('\tSynonyms:')) + '</span></b>'))
                        label.set_alignment(0.0, 0.5)
                        label.show()
                        eventbox = gtk.EventBox()
                        eventbox.set_visible_window(True)
                        eventbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#5C97BF"))
                        #eventbox.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
                        eventbox.add(label)
                        eventbox.show()
                        frame.add(eventbox)
                        frame.show()
                        hbox = gtk.HBox()
                        label = gtk.Label(' '*5)
                        label.show()
                        hbox.pack_start(label, False)
                        hbox.pack_start(frame)
                        hbox.show()
                        vbox1.pack_start(hbox, False)
        except:
            pass
        if wik != u'':
            t = wik.split('\n')
            table = gtk.Table(1, 2)
            table.set_col_spacing(0, 5)
            table.show()
            self.vbox8.pack_start(table, False)
            i = 0
            h1 = []
            j = 0
            for x in t:
                if x.startswith('#'):
                    eventb = gtk.EventBox()
                    eventb.set_visible_window(True)
                    eventb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#AED6EF"))
                    eventb.show()
                    main_label = gtk.Label()
                    main_label.set_markup('<b>'+x.lstrip('#')+'</b>')
                    main_label.set_alignment(0.1, 0)
                    main_label.set_line_wrap(True)
                    main_label.show()
                    table.attach(main_label, 0, 1, i, i+1, xoptions=gtk.FILL)
                    main_frame = gtk.Frame()
                    main_frame.show()
                    main_vbox = gtk.VBox()
                    main_vbox.show()
                    main_frame.add(main_vbox)
                    sub_vbox = gtk.VBox()
                    sub_vbox.show()
                    main_vbox.pack_start(sub_vbox, False)
                    label = gtk.Label(' ')
                    label.show()
                    label.set_alignment(0, 0.5)
                    eventb.add(label)
                    sub_vbox.pack_start(eventb, False)
                    table.attach(main_frame, 1, 2, i, i+1)
                    table.set_row_spacing(i, 10)
                    table.set_col_spacing(0, 5)
                    i = i + 1
                elif not x.startswith('\t') and not x.startswith('#') and not x.startswith('\t#'):
                    s = label.get_text()
                    if x == u'':
                        label.set_text( s + '\n' + x)
                    else:
                        label.set_text(s + x)
                    label.set_width_chars(((40)))
                    label.set_line_wrap(True)
                elif x.startswith('\t#'):
                    eventb = gtk.EventBox()
                    eventb.set_visible_window(True)
                    eventb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#AED6EF"))
                    eventb.show()
                    sub_sub_vbox = gtk.VBox()
                    sub_sub_vbox.show()
                    hbox = gtk.HBox()
                    hbox.show()
                    sub_sub_label = gtk.Label('\t')
                    sub_sub_label.show()
                    hbox.pack_start(sub_sub_vbox, False)
                    sub_sub_vbox.pack_start(sub_sub_label, False)
                    sub_sub_frame = gtk.Frame(' ')
                    
                    label_ = sub_sub_frame.get_label_widget()
                    label_.set_markup('<b>'+x.lstrip('\t#')+'</b>')
                    label_.set_alignment(0, 0.5)
                    try:
                        if sub_sub_frame.get_label_widget()!=NULL:
                            sub_sub_frame.set_label_widget(label_)
                    except:
                        pass
                    sub_sub_frame.show()
                    sub_label = gtk.Label('')
                    sub_label.show()
                    sub_sub_sub_vbox = gtk.VBox()
                    sub_sub_sub_vbox.show()
                    sub_sub_frame.add(sub_sub_sub_vbox)
                    eventb.add(sub_label)
                    sub_label.set_alignment(0,0.5)
                    sub_label.set_use_markup(True)
                    
                    sub_sub_sub_vbox.pack_start(eventb, False)
                    hbox.pack_start(sub_sub_frame)
                    sub_vbox.pack_start(hbox, False)
                    
                elif x.startswith('\t') and not x.startswith('\t#') and not x.startswith('\t\t'):
                    if sub_label.get_use_markup() == False:
                        sub_label.set_use_markup(True)
                    if x == '\t':
                        sub_label.set_label(sub_label.get_text() + '\n' + x)
                    else:
                        x = x.lstrip('\t')
                        if len(x)>1:
                            x.lstrip()
                            #print x[0:2]
                            if x[0].isdigit():
                                sub_label.set_label(sub_label.get_label()+'<b>'+x[0:2]+'</b>'+x[2:len(x)])
                            else:
                                sub_label.set_label(sub_label.get_label()+x)
                    sub_label.set_width_chars(((40)))
                    sub_label.set_line_wrap(True)
                    pass
                elif x.startswith('\t\t#'):
                    eventb = gtk.EventBox()
                    eventb.set_visible_window(True)
                    eventb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#AED6EF"))
                    eventb.show()
                    sub_sub_sub_frame = gtk.Frame(' ')
                    label = sub_sub_sub_frame.get_label_widget()
                    label.set_markup('<b>'+x.lstrip('\t\t#')+'</b>')
                    label.set_label = label.get_label().strip()
                    try:
                        if sub_sub_sub_frame.get_label_widget()!=NULL:
                            sub_sub_sub_frame.set_label_widget(label)
                    except:
                        pass
                    sub_sub_sub_frame.show()
                    sub_sub_sub_sub_vbox = gtk.VBox()
                    sub_sub_sub_sub_vbox.show()
                    sub_sub_sub_vbox.pack_start(sub_sub_sub_frame, False)
                    sub_sub_sub_frame.add(sub_sub_sub_sub_vbox)
                    sub_sub_label = gtk.Label(' ')
                    sub_sub_label.set_alignment(0,0.5)
                    eventb.add(sub_sub_label)
                    sub_sub_label.show()
                    sub_sub_sub_sub_vbox.pack_start(eventb, False)

                elif x.startswith('\t\t') and not x.startswith('\t\t#'):
                    if x.strip('\t\t') !='':
                        if x.find('terms derived from')>=0:
                            sub_sub_label.set_text( sub_sub_label.get_text()+'\n'+ x.lstrip('\t\t'))
                        else:
                            sub_sub_label.set_text( sub_sub_label.get_text()+'\n'+ x.lstrip('\t\t'))
                        sub_sub_label.set_width_chars(((40)))
                        sub_sub_label.set_line_wrap(True)

        try:
            if ws != u'' and ws !=None:
                self.builder.get_object('label10').hide()
                self.builder.get_object('label9').hide()
                #self.builder.get_object('look_webster').set_sensitive(False)
                self.builder.get_object('scrolledwindow7').show()
                ws_table = gtk.Table(columns=2)
                ws_table.show()
                self.vbox13.pack_start(ws_table, False, padding = 5)
                k = 0
                #label = self.builder.get_object('label13')
                #label.set_alignment(0.10, 0.10)
                #label.set_text(ws)
                t = ws.split('\n\n')


                #vbox = self.builder.get_object('vbox13')
                #children = vbox.get_children()
                #for i in children:
                #    vbox.remove(i)
                #print t
                for i in t:
                    if not i.startswith(' '):
                        frame = gtk.Frame('')
                        sub_vbox = gtk.VBox()
                        sub_vbox.show()
                        frame.show()
                        frame.add(sub_vbox)
                        s = i.split('\n')
                        
                        for j in s:
                            if j==u'' or j.find('            ')>=0:
                                pass
                            elif not j.startswith(' ') and j.strip()!='':
                                #print [j[0:5]]
                                try:
                                    type = j.split(',')[1].split('[')[0]
                                except:
                                    pass
                                #print type
                                label = gtk.Label()
                                try:
                                    label.set_markup('<b>'+type+'</b>')
                                except:
                                    pass
                                label.set_line_wrap(True)
                                label.set_alignment(0, 0)
                                label.show()
                                ws_table.attach(label, 0, 1, k, k+1, xoptions = gtk.FILL)
                                frame = gtk.Frame()
                                frame.set_shadow_type(gtk.SHADOW_OUT)
                                frame.show()
                                ws_table.attach(frame, 1, 2, k, k+1)
                                vbox = gtk.VBox()
                                vbox.show()

                                ws_table.set_row_spacing(k,10)
                                ws_table.set_col_spacing(0,5)
                                k = k + 1
                                #event = gtk.EventBox()
                                #event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#AED6EF'))
                                #event.show()
                                label = gtk.Label('')
                                label.set_alignment(0, 0)
                                label.set_line_wrap(True)
                                #label.set_selectable(True)
                                label.show()
                                #event.add(vbox)
                                frame.add(vbox)
                                vbox.pack_start(label, False)
                                #print vbox
                            elif j.startswith('  '):
                                try:
                                    if j.strip()[0].isdigit():

                                        hbox = gtk.HBox()
                                        hbox.show()

                                        label = gtk.Label(' '*10)
                                        label.show()
                                        hbox.pack_start(label, False)

                                        label = gtk.Label()
                                        label.show()
                                        label.set_alignment(0, 0)
                                        label.set_line_wrap(True)
                                        #label.set_selectable(True)
                                        event = gtk.EventBox()
                                        event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#AED6EF'))
                                        event.show()
                                        label = gtk.Label('')
                                        label.set_alignment(0, 0)
                                        label.set_line_wrap(True)
                                        #label.set_selectable(True)
                                        label.show()
                                        event.add(label)
                                        frame = gtk.Frame()
                                        frame.add(event)
                                        frame.set_shadow_type(gtk.SHADOW_OUT)
                                        frame.show()
                                        hbox.pack_start(frame)
                                        vbox.pack_start(hbox,padding = 5)
                                        #sub_vbox.pack_start(event, padding=5)
                                except:
                                    pass
                            if j!=u'':
                                label.set_text(label.get_text()+'\n'+j)
                                label.set_line_wrap(True)
                        #self.vbox13.pack_start(frame, padding=5)
                        self.vbox13.show_all()
                    self.builder.get_object('look_webster').set_sensitive(False)
                    #label = self.builder.get_object('label13')
                    #label.set_alignment(0.10, 0.10)
                    #label.set_text(ws)
            else:
                self.builder.get_object('look_webster').set_sensitive(True)
                self.builder.get_object('label9').show()
                self.builder.get_object('label10').hide()
                self.builder.get_object('scrolledwindow7').hide()
                    
        except:
            pass
    def on_delete_clicked(self, widget=None, event=None):
        if self.tree_value in wordz_db.list_groups():
            wordz_db.delete_group(self.tree_value)
        else:
            wordz_db.delete_word(self.tree_value)
            #self.get_group.remove_text(sel)
        self.treestore.remove(self.iter)
        #buff = self.output_txtview.get_buffer()
        #buff.set_text('')
        #self.output_txtview.set_buffer(buff)
        get_group_ch = self.get_group.child
        group = get_group_ch.get_text()
        self.refresh_groups(group, 1)
        self.frame2.hide()
        #self.frame4.hide()
        self.welcome.show()
        self.note.set_markup('<span foreground="white"><b>Nothing selected</b></span>')
        #self.hbox2.pack_start(self.welcome)
        self.play_b.set_sensitive(False)
        self.delete_b.set_sensitive(False)

    def on_edit_clicked(self, widget=None, event=None):
        self.output_txtview.set_editable(True)

    def on_save_clicked(self, widget=None, event=None):
        buff = self.output_txtview.get_buffer()
        start = buff.get_iter_at_offset(0)
        end = buff.get_iter_at_offset(-1)
        new_details = buff.get_text(start, end)
        wordz_db.update_details(self.tree_value, new_details)
        #self.output_txtview.set_editable(False)

    def item_list_changed(self, widget=None, event=None):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == "Return":
            self.get_group.append_text(widget.get_text())
            widget.set_text("")

    def on_MainWindow_destroy(self, widget, data=None):
        gtk.main_quit()

    def on_add_clicked(self, widget, data=None):
	word = self.get_word.get_text()
        self.new_word = []
        if word not in self.new_word and word not in wordz_db.list_words():
            self.new_word.append(word)

        get_group_ch = self.get_group.child
        group = get_group_ch.get_text()
        conts = self.details.get_buffer()
        start = conts.get_iter_at_offset(0)
        end = conts.get_iter_at_offset(-1)
        detail = conts.get_text(start, end)
        wordz_db.add_to_db(word, group, detail)
        self.refresh_groups(group)
        self.treestore.clear()
        #print self.new_word
        self.on_back_clicked()

    def item_list_changed(self, widget=None, event=None):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == "Return":
            self.item_list.append_text(widget.get_text())
            widget.set_text('')

    def refresh_groups(self, grp, flag=0):
        tmp = wordz_db.list_groups()
        n = len(tmp)
        for i in range(0,n+flag):
            self.get_group.remove_text(0)
        for x in tmp:
            self.get_group.append_text(x)

    def on_about_clicked(self, widget, data=None):
        dialog = gtk.AboutDialog()
        dialog.set_name(_('wordz'))
        dialog.set_copyright('(c) 2010 Ratnadeep Debnath')
        dialog.set_website('http://gitorious.org/wordGroupz/wordgroupz')
        dialog.set_authors(['Ratnadeep Debnath <rtnpro@gmail.com>'])
        dialog.set_program_name(_('wordGroupz '+ VERSION))
        dialog.run()
        dialog.destroy()


    def on_back_clicked(self, widget=None, data=None):
        if self.search.get_text()!= '':
            self.frame2.hide()
            self.frame4.hide() 
            self.search.set_text('')
            self.welcome.show()
            self.frame4.hide() 
            self.note.set_alignment(0.5, 0.1)
            self.note.set_markup('<span foreground="white"><b>Nothing selected</b></span>')
            return
        self.treestore.clear()
        #self.search.set_text('')
        #self.new_word = []
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        c.execute("""select word, accuracy from word_groups""")
        self.ls = []
        self.ls = c.fetchall()
        #print 'l', self.ls
        c.close()
        self.acc_dict = {}
        for i in self.ls:
            if i[1] == u'0:0':
                self.acc_dict[i[0]] = 0
                #if i[0] not in self.new_word:
                #    self.new_word.append(i[0])
            else:
                #try:
                    #self.new_word.remove(i[0])
                #except:
                #    pass
                t = i[1].split(':')
                acc = float(t[0])/float(t[1])*100
                acc = int(acc)
                self.acc_dict[i[0]] = acc

        for group in wordz_db.list_groups():
            l = wordz_db.list_words_per_group(group)
            t = 0
            count = 0
            for i in l:
                if i not in self.new_word:
                    #print i
                    t = t + self.acc_dict[i]
                    count = count + 1
            if count != 0:
                t = t/count
            else:
                t = 0
            piter = self.treestore.append(None, [group, t])
            #print self.new_word
            for word in wordz_db.list_words_per_group(group):
                self.treestore.append(piter, [word, self.acc_dict[word]])
        self.treeview.expand_all()
        #buff = self.output_txtview.get_buffer()
        #buff.set_text('Nothing selected')
        #self.output_txtview.set_buffer(buff)
        self.selected_word.set_text('')
        #self.show_details_tree()
        #self.selected_word.hide()
        self.frame2.hide()
        self.frame4.hide()
        self.welcome.show()
        self.note.set_alignment(0.5, 0.1)
        self.note.set_markup('<span foreground="white"><b>Nothing selected</b></span>')
        

        self.play_b.set_sensitive(False)
        self.delete_b.set_sensitive(False)


    def on_get_details_clicked(self, widget, data=None):
        word = self.get_word.get_text()
        dic = self.chose_dict.get_active_text()
        if dic == 'online webster':
            d = online_dict()
            defs = '\n' + '='*10 + '\n' + d.get_def(word)
            defs = 'from online webster:\n' + defs
        elif dic == 'offline wordnet':
            defs = '\n' + '='*10 + '\n' + wordnet.get_definition(word)
        buff = self.details.get_buffer()
        buff.set_text(defs)
        self.details.set_buffer(buff)
        
            

    #def on_get_details1_clicked(self, widget, data=None):
        #thread.start_new_thread(self.on_get_details1_clicked,(self,''))
        """word = self.tree_value
        dic = self.chose_dict.get_active_text()
        #print dic
        if dic == 'webster':
            #print wordz_db.check_ws(self.tree_value)
            if wordz_db.check_ws(self.tree_value):
                defs = wordz_db.get_dict_data(dic, self.tree_value)[0]
            else:
                d = online_dict()
                defs = d.get_def(word)
                wordz_db.save_webster(self.tree_value, defs)
            defs = '\n' + "webster:\n" + defs + '\n'
        elif dic == 'wordnet':
            if wordz_db.check_wn(self.tree_value):
                defs = wordz_db.get_dict_data(dic, self.tree_value)[0]
            else:
                defs = wordnet.get_definition(word)
            defs = '\n' + 'wordnet:\n' + defs + '\n'
        elif dic == 'wiktionary':
            #print  wordz_db.check_wik(self.tree_value)
            if wordz_db.check_wik(self.tree_value):
                defs = wordz_db.get_dict_data(dic, self.tree_value)[0].strip("'").strip('"')
                defs = '\n' + 'wiktionary:\n'+defs + '\n'
            else:
                defs = ''
        buff = self.output_txtview.get_buffer()
        end = buff.get_iter_at_offset(-1)
        buff.place_cursor(end)
        buff.insert_interactive_at_cursor(defs, True)"""
    def on_lookup_webster_clicked(self, widget=None, event=None):
        self.builder.get_object('look_webster').set_sensitive(False)
        self.builder.get_object('label9').hide()
        self.builder.get_object('label10').show()
        threading.Thread(target=self._startthread).start()

    def _startthread(self):
        word = self.tree_value
        dic = 'webster'
        if wordz_db.check_ws(win.tree_value):
            defs = wordz_db.get_dict_data(dic, win.tree_value)[0]
        else:
            d = online_dict()
            defs = d.get_def(word)
            
            wordz_db.save_webster(win.tree_value, defs)
        defs = '\n' + "webster:\n" + defs + '\n'
        #print defs
        self.builder.get_object('look_webster').set_sensitive(True)
        self.show_details_tree()

    def on_show_stats_clicked(self, widget=None, event=None):
        pass
        '''
        #code for generating accuracy bar chart
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        c.execute("""select word, accuracy from word_groups""")
        l = c.fetchall()
        #print l
        c.close()
        conn.close()

        N = len(l)
        words = ()
        val = ()
        err = ()
        for i in l:
            words = words + (i[0],)
            t = i[1].split(':')
            if i[1]=='0'or i[1]== '0:0':
                h = 0.0
            else:
                h = (float(t[0])/float(t[1]))*100
            val = val + (h,)
            err = err + (0,)

        #print words, val, err
        ind = np.arange(N)  # the x locations for the groups
        width = 0.40       # the width of the bars

        fig = plt.figure()
        ax = fig.add_subplot(111)
        rects1 = ax.bar(ind, val, width, color='g')
        ax.set_ylabel('Accuracy')
        ax.set_title('Accuracy for words', bbox = {'facecolor':'0.8', 'pad':5})
        ax.set_xticks(ind+width)
        ax.set_xticklabels( words )

        def autolabel(rects):
            # attach some text labels
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                        ha='center', va='bottom')
        canvas = FigureCanvasGTK(fig)
        canvas.set_size_request(100*len(words),((40))0)
        canvas.show()
        autolabel(rects1)
        graphwin = gtk.Window()
        graphwin.set_default_size(600, ((40))0)
        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox = gtk.VBox()
        vbox.show()
        scroller.add_with_viewport(canvas)
        #vbox.pack_start(scroller)
        canvas.show()
        graphwin.add(scroller)
        graphwin.show_all()'''
if __name__ == "__main__":
    wordz_db=wordGroupzSql()
    wordz_db.db_init()
    win = wordzGui()
    win.window.show()
    gtk.gdk.threads_init()
    gtk.main()
