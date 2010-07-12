#!/usr/bin/env python
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

import pygtk
import gtk
import sqlite3
import os
import sys
import socket
import string
import nltk_wordnet as wordnet

usr_home = os.environ['HOME']
wordgroupz_dir = usr_home+'/.wordgroupz'
db_file_path = wordgroupz_dir+'/wordz'

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
            (word text, grp text, details text)''')
        #if not 'groups' in tables:
         #   c.execute('''create table groups
          #  (grp text)''')
        conn.commit()
        c.close()
        conn.close()

    def list_groups(self):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        groups = []
        for row in c.execute("""select grp from groups order by grp"""):
            if row[0] is not u'':
                groups.append(row[0])
        c.close()
        return groups

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


    def add_to_db(self,word, grp, detail):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        conn.text_factory = str
        t = (grp,)
        if grp not in self.list_groups() and grp is not '':
            c.execute("""insert into groups values (?)""",t)
            conn.commit()
        if word is not '' and word not in self.list_words_per_group(grp) and grp is not '':
            t = (word, grp, detail)
            c.execute('''insert into word_groups
                values(?,?,?)''', t)
            conn.commit()
        c.close()

    def get_details(self,selection):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (selection, )
        if selection in self.list_groups() or selection is '':
            return "No word selected"
        else:
            result = c.execute("""select word,grp,details from word_groups where word=?""",t)
            tmp = result.fetchone()
            return tmp[2]

    def update_details(self,tree_value, details):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (tree_value,)
        c.execute("""update word_groups set details='%s' where word=?"""% (details),t)
        conn.commit()
        c.close()

    def delete_word(self, tree_value):
        conn = sqlite3.connect(db_file_path)
        c = conn.cursor()
        t = (tree_value,)
        c.execute("""delete from word_groups where word=?""",t)
        conn.commit()
        c.close()

class online_dict:
    def __init__(self, addr = 'tcp!dict.org!2628'):
        self.sock = self.dial(addr)
        self.f = self.sock.makefile("r")
        welcome = self.f.readline()
        if welcome[0:4] != '220 ':
            raise Exception("server doesn't want you (%s)" % welcome[0:4])
        r, _ = self._cmd('CLIENT python client, versionless')
        if r != '250':
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
        if line[0:4] != '250 ':
            raise Exception('expected code 250 after match (%s)' % line)
        return lines
    
    def get_def(self, word):
        l = self.match(word, db='!', strat='exact')
        for db, word in l:
            defs = self.definition(word, db=db)
            if defs == []:
                print >> sys.stderr, 'no-match'
                return 2
            db, dbdescr, defstr = defs[0]
            s = '\n\n\n'.join([defstr for _, _, defstr in defs])
        return s
    

class wordzGui:
    wordz_db=wordGroupzSql()
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("wordgroupz.glade")
        self.window = self.builder.get_object("MainWindow")
        self.window.set_icon_from_file("/usr/share/pixmaps/wordgroupz.png")
        self.window.set_title("wordGroupz")
        self.builder.connect_signals(self)
        self.get_word = self.builder.get_object("get_word")
        self.get_group = gtk.combo_box_entry_new_text()
        self.get_group.set_tooltip_text("Enter a group for your word")
        self.details = self.builder.get_object("textview1")
        self.get_group.child.connect('key-press-event',self.item_list_changed)
        self.vpan = self.builder.get_object("vpaned1")
        self.output_txtview = self.builder.get_object("textview2")
        for x in wordz_db.list_groups():
            self.get_group.append_text(x)
        self.table1 = self.builder.get_object("table1")
        self.get_group.show()
        self.table1.attach(self.get_group, 1,2,1,2)

        self.hbox3 = self.builder.get_object("hbox3")
        self.hbox3.hide()
        self.treestore = gtk.TreeStore(str)
        for group in wordz_db.list_groups():
            piter = self.treestore.append(None, [group])
            for word in wordz_db.list_words_per_group(group):
                self.treestore.append(piter, [word])
        self.treeview = gtk.TreeView(self.treestore)
        self.tvcolumn = gtk.TreeViewColumn('Word Groups')
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.treeview.set_reorderable(True)
        self.selection = self.treeview.get_selection()
        self.selection.connect('changed', self.tree_select_changed)
        self.treeview.set_tooltip_text("Shows words classified in groups")
        self.treeview.show()
        self.scrolledwindow1 = self.builder.get_object("scrolledwindow1")
        self.scrolledwindow1.add_with_viewport(self.treeview)
        self.search=self.builder.get_object("search")
        self.search.connect('changed',self.on_search_changed)

        self.chose_dict_hbox = self.builder.get_object('hbox6')
        self.chose_dict = gtk.combo_box_new_text()
        for dict in ['online webster', 'offline wordnet']:
            self.chose_dict.append_text(dict)
        self.chose_dict.set_active(1)
        self.chose_dict.show()
        self.chose_dict_hbox.pack_start(self.chose_dict, True, True, padding = 5)
    
    def on_search_changed(self,widget=None,event=None):
        search_txt = self.search.get_text()
        words = list
        self.treestore.clear()
        for group in wordz_db.list_groups():
            if search_txt in wordz_db.list_words_per_group(group):
                piter = self.treestore.append(None, [group])
                for word in wordz_db.list_words_per_group(group):
                    self.treestore.append(piter, [word])

    def tree_select_changed(self, widget=None, event=None):
        self.model, self.iter = self.selection.get_selected()
        if self.iter is not None:
            self.tree_value = self.model.get_value(self.iter,0)

            if self.tree_value not in wordz_db.list_groups():
                self.hbox3.show()
                w, h = self.window.get_size()
                self.vpan.set_position(h)
                tmp = self.vpan.get_position()
                self.vpan.set_position(int((240.0/450)*h))
            else:
                self.vpan.set_position(10000)
                self.hbox3.hide()
            if self.output_txtview.get_editable():
                self.output_txtview.set_editable(False)
            detail = wordz_db.get_details(self.tree_value)
            buff = self.output_txtview.get_buffer()
            buff.set_text(detail)
            self.output_txtview.set_buffer(buff)

    def on_delete_clicked(self, widget=None, event=None):
        wordz_db.delete_word(self.tree_value)
        self.treestore.remove(self.iter)

    def on_edit_clicked(self, widget=None, event=None):
        self.output_txtview.set_editable(True)

    def on_save_clicked(self, widget=None, event=None):
        buff = self.output_txtview.get_buffer()
        start = buff.get_iter_at_offset(0)
        end = buff.get_iter_at_offset(-1)
        new_details = buff.get_text(start, end)
        wordz_db.update_details(self.tree_value, new_details)
        self.output_txtview.set_editable(False)

    def item_list_changed(self, widget=None, event=None):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == "Return":
            self.get_group.append_text(widget.get_text())
            widget.set_text("")

    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()

    def on_add_clicked(self, widget, data=None):
        word = self.get_word.get_text()
        get_group_ch = self.get_group.child
        group = get_group_ch.get_text()
        conts = self.details.get_buffer()
        start = conts.get_iter_at_offset(0)
        end = conts.get_iter_at_offset(-1)
        detail = conts.get_text(start, end)
        wordz_db.add_to_db(word, group, detail)
        self.refresh_groups(group)
        self.treestore.clear()
        for group in wordz_db.list_groups():
            piter = self.treestore.append(None, [group])
            for word in wordz_db.list_words_per_group(group):
                self.treestore.append(piter, [word])

    def item_list_changed(self, widget=None, event=None):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == "Return":
            self.item_list.append_text(widget.get_text())
            widget.set_text('')

    def refresh_groups(self, grp):
        tmp = wordz_db.list_groups()
        n = len(tmp)
        for i in range(0,n):
            self.get_group.remove_text(0)
        for x in tmp:
            self.get_group.append_text(x)

    def on_about_clicked(self, widget, data=None):
        dialog = gtk.AboutDialog()
        dialog.set_name('wordz')
        dialog.set_copyright('(c) 2010 Ratnadeep Debnath')
        dialog.set_website('http://gitorious.org/wordGroupz/wordgroupz')
        dialog.set_authors(['Ratnadeep Debnath <rtnpro@gmail.com>'])
        dialog.set_program_name('wordGroupz')
        dialog.run()
        dialog.destroy()


    def on_back_clicked(self, widget, data=None):
        self.treestore.clear()
        for group in wordz_db.list_groups():
            piter = self.treestore.append(None, [group])
            for word in wordz_db.list_words_per_group(group):
                self.treestore.append(piter, [word])

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
        
            

    def on_get_details1_clicked(self, widget, data=None):
        word = self.tree_value
        dic = self.chose_dict.get_active_text()
        print dic
        if dic == 'online webster':
            d = online_dict()
            defs = d.get_def(word)
            defs = '\n' + '='*10 + '\n' + "\nfrom online webster:\n" + defs
        elif dic == 'offline wordnet':
            defs = '\n' + '='*10 + '\n' + wordnet.get_definition(word)
        buff = self.output_txtview.get_buffer()
        end = buff.get_iter_at_offset(-1)
        buff.place_cursor(end)
        buff.insert_interactive_at_cursor(defs, True)


if __name__ == "__main__":
    wordz_db=wordGroupzSql()
    wordz_db.db_init()
    win = wordzGui()
    win.window.show()
    gtk.main()
