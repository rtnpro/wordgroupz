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

usr_home = os.environ['HOME']
wordgroupz_dir = usr_home+'/.wordgroupz'
db_file_path = wordgroupz_dir+'/wordz'

def db_init():
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
    if not 'groups' in tables:
        c.execute('''create table groups
        (grp text)''')
    conn.commit()
    c.close()
    conn.close()

def list_groups():
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    groups = []
    for row in c.execute("""select grp from groups order by grp"""):
        if row[0] is not u'':
            groups.append(row[0])
    c.close()
    print groups
    return groups

def list_words_per_group(grp):
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    words = []
    t = (grp,)
    for row in c.execute("""select word from word_groups where grp=?""",t):
        if row[0] != '':
            words.append(row[0])
    c.close()
    return words


def add_to_db(word, grp, detail):
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    conn.text_factory = str
    t = (grp,)
    if grp not in list_groups() and grp is not '':
        c.execute("""insert into groups values (?)""",t)
        conn.commit()
    if word is not '' and word not in list_words_per_group(grp) and grp is not '':
        t = (word, grp, detail)
        c.execute('''insert into word_groups
            values(?,?,?)''', t)
        conn.commit()
    c.close()

def get_details(selection):
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    t = (selection, )
    print selection
    if selection in list_groups() or selection is '':
        return "No word selected"
    else:
        result = c.execute("""select word,grp,details from word_groups where word=?""",t)
        tmp = result.fetchone()
        print tmp
        return tmp[2]


class wordzGui:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("wordgroupz.glade")
        self.window = self.builder.get_object("MainWindow")
        self.window.set_icon_from_file("/usr/share/pixmaps/wordgroupz.png")
        self.window.set_title("wordGroupz")
        self.builder.connect_signals(self)
        self.get_word = self.builder.get_object("get_word")
        self.get_group = gtk.combo_box_entry_new_text()
        self.details = self.builder.get_object("textview1")
        self.get_group.child.connect('key-press-event',self.item_list_changed)
        self.vpan = self.builder.get_object("vpaned1")
        self.output_txtview = self.builder.get_object("textview2")
        for x in list_groups():
            self.get_group.append_text(x)
        self.table1 = self.builder.get_object("table1")
        self.get_group.show()
        self.table1.attach(self.get_group, 1,2,1,2)

        self.treestore = gtk.TreeStore(str)
        for group in list_groups():
            piter = self.treestore.append(None, [group])
            for word in list_words_per_group(group):
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
        #self.selection.set_select_function(self.on_tree_select, data=None)
        self.selection.connect('changed', self.tree_select_changed)
        self.scrolledwindow1 = self.builder.get_object("scrolledwindow1")
        self.scrolledwindow1.add_with_viewport(self.treeview)
        self.search=self.builder.get_object("search")
        self.search.connect('changed',self.on_search_changed)

    def on_search_changed(self,widget=None,event=None):
        search_txt = self.search.get_text()
        groups = list_groups()
        words = list
        self.treestore.clear()
        for group in groups:
            if search_txt in list_words_per_group(group):
                piter = self.treestore.append(None, [group])
                for word in list_words_per_group(group):
                    self.treestore.append(piter, [word])

    def tree_select_changed(self, widget=None, event=None):
        model, iter = self.selection.get_selected()
        value = model.get_value(iter,0)
        #print value
        if value not in list_groups():
            self.vpan.set_position(275)
        else:
            self.vpan.set_position(10000)
        detail = get_details(value)
        buff = self.output_txtview.get_buffer()
        buff.set_text(detail)
        self.output_txtview.set_buffer(buff)



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
        #print group
        add_to_db(word, group, detail)
        self.refresh_groups(group)
        self.treestore.clear()
        for group in list_groups():
            piter = self.treestore.append(None, [group])
            for word in list_words_per_group(group):
                self.treestore.append(piter, [word])

    def item_list_changed(self, widget=None, event=None):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == "Return":
            self.item_list.append_text(widget.get_text())
            widget.set_text('')

    def refresh_groups(self, grp):
        self.get_group.append_text(grp)

    def on_about_clicked(self, widget, data=None):
        dialog = gtk.AboutDialog()
        dialog.set_name('wordz')
        dialog.set_copyright('(c) 2010 Ratnadeep Debnath')
        dialog.set_website('http://gitorious.org/wordGroupz/wordgroupz')
        dialog.set_authors(['Ratnadeep Debnath <rtnpro@gmail.com>'])
        dialog.set_program_name('wordGroupz')
        dialog.run()
        dialog.destroy()

    def on_find_clicked(self, widget, data=None):
        search = self.builder.get_object("search")
        search_txt = search.get_text()
        groups = list_groups()
        words = list
        self.treestore.clear()
        for group in groups:
            if search_txt in list_words_per_group(group):
                piter = self.treestore.append(None, [group])
                for word in list_words_per_group(group):
                    self.treestore.append(piter, [word])

    def on_back_clicked(self, widget, data=None):
        self.treestore.clear()
        for group in list_groups():
            piter = self.treestore.append(None, [group])
            for word in list_words_per_group(group):
                self.treestore.append(piter, [word])


if __name__ == "__main__":
    db_init()
    win = wordzGui()
    win.window.show_all()
    gtk.main()
