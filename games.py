# games.py
import pygtk
import gtk
import wordgroupz
import random

import locale
import gettext
APP = 'worgroupz'
DIR = 'locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

class games_GUI:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file('games.glade')
        self.builder.connect_signals(self)
        self.window = self.builder.get_object('games')
        self.flash_data = db.get_details_for_flashcard()
        for i in self.flash_data:
            if i[1] == '':
                self.flash_data.remove(i)
        self.flash_frame = self.builder.get_object('frame5')
        self.flash_label = self.builder.get_object('label24')
        self.eventbox4 = self.builder.get_object('eventbox4')
        self.eventbox4.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#444444"))
        #self.eventbox6 = self.builder.get_object('eventbox6')
        #self.eventbox6.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#F4F2EE'))
        self.eventbox10 = self.builder.get_object('eventbox10')
        self.eventbox10.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        label=self.flash_frame.get_label_widget()
        label.set_text(_('word'))
        label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        try:
            if self.flash_frame.get_label_widget()!=NULL:
                self.flash_frame.set_label_widget(label)
        except:
            pass
        self.current_index = 0
        try:
            self.flash_label.set_markup('<big><big><b>'+self.flash_data[self.current_index][0]+'</b></big></big>')
        except:
            pass
        self.check = self.builder.get_object('check')
        self.total_count = len(self.flash_data)
        self.count = 0
        self.total_count_label = self.builder.get_object('label26')
        self.correct_label = self.builder.get_object('label27')
        self.incorrect_label = self.builder.get_object('label28')
        self.total_count_label.set_text(str(self.total_count))
        self.radio_word = self.builder.get_object('byword1')
        self.radio_definition = self.builder.get_object('bydefinition1')
        self.check_random = self.builder.get_object('random1')
        self.button_iknow = self.builder.get_object('iknow1')
        self.button_idunno = self.builder.get_object('idunno1')
        self.button_check = self.builder.get_object('check1')
        #self.check.connect('clicked', self.on_check_clicked)
        self.correct = []
        self.incorrect = []
        self.correct_no = 0
        self.incorrect_no = 0
        self.mode='word'
        self.question = self.builder.get_object('label6')
        self.option=[]
        self.option0 = self.builder.get_object('option0')
        self.accuracy = self.get_accuracy_table()
        accuracy = {}
        for i in self.accuracy.keys():
            if self.accuracy[i][1]!=0:
                val = float(self.accuracy[i][0])/self.accuracy[i][1]
            else:
                val = 0
            accuracy[i] = val
        accuracy_ = []
        for key, value in sorted(accuracy.iteritems(), key=lambda (k,v): (v,k)):
            accuracy_.append(key)
        
        self.sorted_accuracy_list = accuracy_
        self.res = ''
        for i in range(1,5):
            self.option.append(self.builder.get_object('option'+str(i)))
        self.mcq_dict = self.get_mcq_data()
        #self.set_up_mcq()
        #self.builder.get_object('label9').set_text(str(len(self.ques.keys())))
        self.proceed_b = self.builder.get_object('proceed')
        self.proceed_b.set_sensitive(False)
        #self.builder.get_object('scrolledwindow2').show()

        #menu - flash games
        self.game_mode = self.builder.get_object('game_mode')
        self.game_mode_sub = gtk.Menu()
        self.game_mode_sub.show()
        self.by_word = gtk.RadioMenuItem(None, _('word'))
        self.by_word.set_active(True)
        self.by_word.show()
        self.by_def = gtk.RadioMenuItem(self.by_word, _('definition'))
        self.by_def.connect('toggled', self.on_radio_toggled)
        self.by_word.connect('toggled', self.on_radio_toggled)
        #self.by_word.set_active(True)
        self.by_def.show()
        #self.by_def = self.by_definition
        self.by_random = gtk.CheckMenuItem('_Random')
        self.by_random.connect('toggled', self.on_random_clicked)
        self.by_random.show()
        self.game_mode_sub.append(self.by_word)
        self.game_mode_sub.append(self.by_def)
        self.game_mode_sub.append(self.by_random)
        self.game_mode.set_submenu(self.game_mode_sub)


        #mcq
        self.eventbox1 = self.builder.get_object('eventbox1')
        self.eventbox1.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#444444'))
        self.eventbox5 = self.builder.get_object('eventbox5')
        self.eventbox5.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        
        self.eventbox8 = self.builder.get_object('eventbox8')
        self.eventbox8.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
        self.review_b = self.builder.get_object('review')
        self.review_data = []
        
    def set_up_mcq(self):
        #d = self.mcq_dict.keys()
        all = self.mcq_dict.keys()
        d = self.sorted_accuracy_list[0:self.no_of_ques]
        random.shuffle(d)
        self.ques = {}
        for i in d:
            opts = []
            opt_keys = [i]
            try:
                a = random.choice(self.mcq_dict[i])
            except:
                continue
            a = a[1:len(a)]
            opts.append(a)
            for j in all:
                if j not in opt_keys:
                    #print 'j:'
                    #print j
                    try:
                        a = random.choice(self.mcq_dict[j])
                    except:
                        continue
                    if a == u'':
                        continue
                    #a = a[1:len(a)]
                    opts.append(a)
                    opt_keys.append(j)
                if len(opt_keys) == 4:
                    break
            random.shuffle(opts)
            self.ques[i] = opts
        self.question.set_markup('<big><big><b>'+self.ques.keys()[0]+'</b></big></big>')
        j=0
        for i in self.option:
            try:
                i.set_label(self.ques[self.question.get_text()][j])
                label = i.get_child()
                label.set_line_wrap(True)
                j = j+1
            except:
                print 'Not enough questions'
        self.mcq_count = 0
        self.response = []
        self.ans = []
        for i in self.ques.keys():
            for j in self.ques[i]:
                for k in self.mcq_dict[i]:
                    if k.find(j)>=0:
                        index = self.mcq_dict[i].index(k)
                        self.ans.append([j,index])
        self.mcq_correct = 0
        self.mcq_incorrect = 0
        self.builder.get_object('label9').set_text(str(len(self.ques.keys())))
    def save_accuracy(self):
        tmp =[]
        for i in self.accuracy[self.ques.keys()[self.mcq_count]]:
            tmp.append(str(i))
        text = ':'.join(tmp)
        db.save_accuracy_for_word(self.ques.keys()[self.mcq_count], text)
        
    def show_graph(self):
        pass

    def on_proceed_clicked(self, widget, event=None):
        if self.mcq_count < len(self.ques.keys()) - 1:
            if self.res[0] != '':
                #print self.ans
                ans_index = self.ques[self.question.get_text()].index(self.ans[self.mcq_count][0])
                self.response.append(self.res)
                if self.response[self.mcq_count][0]==self.ans[self.mcq_count][0]:
                    self.mcq_correct = self.mcq_correct + 1
                    self.accuracy[self.ques.keys()[self.mcq_count]][0] = self.accuracy[self.ques.keys()[self.mcq_count]][0] + 1
                    self.accuracy[self.ques.keys()[self.mcq_count]][1] = self.accuracy[self.ques.keys()[self.mcq_count]][1] + 1
                    self.review_data = self.review_data + [(self.mcq_count + 1, self.ques.keys()[self.mcq_count], ans_index+1, self.res[1]+1, gtk.STOCK_APPLY)]
                    
                else:
                    self.mcq_incorrect = self.mcq_incorrect +1
                    self.accuracy[self.ques.keys()[self.mcq_count]][1] = self.accuracy[self.ques.keys()[self.mcq_count]][1] + 1
                    self.review_data = self.review_data + [(self.mcq_count + 1, self.ques.keys()[self.mcq_count], ans_index+1, self.res[1]+1, gtk.STOCK_CLOSE)]
                self.save_accuracy()
                self.mcq_count = self.mcq_count + 1
                try:
                    self.question.set_markup('<big><big><b>'+self.ques.keys()[self.mcq_count]+'</b></big></big>')
                except:
                    #print 'out of index error line 187'
                    pass

                j = 0
                for i in self.option:
                    try:
                        i.set_label(self.ques[self.question.get_text()][j])
                        label = i.get_child()
                        label.set_line_wrap(True)
                        j = j+1
                    except:
                        print 'Not enough questions'

        else:
            if self.res[0] != '':
                #print 'Heya'
                #print self.res
                #print 'HI'
                ans_index = self.ques[self.question.get_text()].index(self.ans[self.mcq_count][0])
                self.response.append(self.res)
                #print self.response
                if self.response[self.mcq_count][0]==self.ans[self.mcq_count][0]:
                    self.mcq_correct = self.mcq_correct + 1
                    #print self.mcq_correct
                    self.accuracy[self.ques.keys()[self.mcq_count]][0] = self.accuracy[self.ques.keys()[self.mcq_count]][0] + 1
                    self.accuracy[self.ques.keys()[self.mcq_count]][1] = self.accuracy[self.ques.keys()[self.mcq_count]][1] + 1
                    self.review_data = self.review_data + [(self.mcq_count + 1, self.ques.keys()[self.mcq_count], ans_index+1, self.res[1]+1, gtk.STOCK_APPLY)]

                else:
                    self.mcq_incorrect = self.mcq_incorrect +1
                    #print self.mcq_incorrect
                    self.accuracy[self.ques.keys()[self.mcq_count]][1] = self.accuracy[self.ques.keys()[self.mcq_count]][1] + 1
                    self.review_data = self.review_data + [(self.mcq_count + 1, self.ques.keys()[self.mcq_count], ans_index+1, self.res[1]+1, gtk.STOCK_CLOSE)]
                self.save_accuracy()
                self.mcq_count = self.mcq_count + 1            
            self.question.set_text('OVER!')
            self.builder.get_object('frame1').hide()
            self.builder.get_object('frame3').hide()
            self.builder.get_object('label33').show()
            self.proceed_b.hide()
            self.review_b.show()
            
            #self.show_graph()
        self.option0.set_active(True)
        self.builder.get_object('label17').set_text(str(self.mcq_correct))
        self.builder.get_object('label18').set_text(str(self.mcq_incorrect))
        self.proceed_b.set_sensitive(False)
        self.res = ['',-1]
        #print self.review_data
        
    def on_review_clicked(self, widget=None, event=None):
        self.review_window = gtk.Window()
        self.review_window.set_title(_('Review'))
        self.review_window.set_icon_from_file("/usr/share/pixmaps/wordgroupz.png")
        self.review_window.set_default_size(500,450)
        list_tree = [_('Q.No.'),_('Question'),_('Answer'),_('Response'), _('Result')]
        list_store = gtk.ListStore(str,str,str,str,str)
        for row in self.review_data:
            #print len(row)
            list_store.append(row)
        review_tree = gtk.TreeView(list_store)
        cell = gtk.CellRendererText()
        cell_pb = gtk.CellRendererPixbuf()
        i=0
        for title in list_tree:
            tvcolumn = gtk.TreeViewColumn(title)
            
            if title == 'Result':
                #cell_data = gtk.CellRendererPixbuf()
                tvcolumn.pack_start(cell_pb, False)
                tvcolumn.set_attributes(cell_pb, stock_id=i)
                

            else:
                cell_data = gtk.CellRendererText()
                tvcolumn.pack_start(cell, True)
                tvcolumn.set_attributes(cell, text=i)
                
            
            review_tree.append_column(tvcolumn)
            i = i+1

        review_tree.set_headers_visible(True)
        scroller = gtk.ScrolledWindow()
        scroller.show()
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        review_tree.show()
        vbox = gtk.VBox()
        vbox.pack_start(scroller)
        vbox.show()
        scroller.add_with_viewport(review_tree)
        self.review_window.set_modal(True)
        self.review_window.add(vbox)
        self.review_window.show_all()
        self.review_window.connect('destroy', self.on_review_win_destroy)

    def on_review_win_destroy(self, widget=None, event=None):
        self.review_window.destroy()
        

    def get_accuracy_table(self):
        ac = {}
        #l = []
        for i in self.flash_data:
            #print 'i ',
            #print i
            l = i[2].split(':')
            #print l
            l[0]=int(l[0])
            l[1]=int(l[1])
            ac[i[0]] = l
        #print ac
        return ac
            
    
    def get_mcq_data(self):
        d = {}
        for i in self.flash_data:
            if i[1]!= u'':
                l = []
                t = i[1].split('\n')
                for x in t:
                    if x.startswith('\t') and not x.startswith('\tSynonyms:'):
                        l.append(x.lstrip('\t')[2:len(x.lstrip('\t'))])
                d[i[0]]=l
        return d
    def on_random_clicked(self, widget=None, event=None):
        if self.current_index <= len(self.flash_data)-2:
            self.remaining = self.flash_data[self.current_index+1:len(self.flash_data)]
        else:
            self.remaining = []
        if self.by_random.get_active():
            random.shuffle(self.remaining)
            self.flash_data = self.flash_data[0:self.current_index+1]+self.remaining
        else:
            self.remaining.sort()
            self.flash_data = self.flash_data[0:self.current_index+1]+self.remaining
            
    def on_opts_toggled(self, widget=None, event=None):
        j = 1
        for i in self.option:
            if i.get_active():
                res = i.get_label()
                #label = i.get_child()
                #res = label.get_text()
                #print res
                index = self.option.index(i)
                self.res = [res,index]
                break
                #print res
        self.proceed_b.set_sensitive(True)
                
    def on_radio_toggled(self, widget=None, event=None):
        for i in [self.by_word, self.by_def]:
            if i.get_active():
                #print i.get_active()
                #print i.get_label()
                self.mode = i.get_label()
                #print self.mode
        if self.mode == 'definition':
            #print self.mode
            label=self.flash_frame.get_label_widget()
            label.set_text(_('definition'))
            label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
            try:
                if self.flash_frame.get_label_widget()!=NULL:
                    self.flash_frame.set_label_widget(label)
            except:
                pass
            self.flash_label.set_text(self.flash_data[self.current_index][1])
            self.flash_label.set_alignment(0.1, 0.1)
        elif self.mode == 'word':
            label=self.flash_frame.get_label_widget()
            label.set_text(_('word'))
            label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
            try:
                if self.flash_frame.get_label_widget()!=NULL:
                    self.flash_frame.set_label_widget(label)
            except:
                pass
            self.flash_label.set_markup('<big><big><b>'+self.flash_data[self.current_index][0]+'</b></big></big>')
            self.flash_label.set_alignment(0.5, 0.5)
    def on_games_destroy(self, widget=None, event=None):
        gtk.main_quit()

    def on_check_clicked(self, widget=None, event=None):
        if self.flash_frame.get_label() == 'word':
            label=self.flash_frame.get_label_widget()
            label.set_markup('definition for <big>' + self.flash_data[self.current_index][0] + '</big>')
            label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
            try:
                if self.flash_frame.get_label_widget!=NULL:
                    self.flash_frame.set_label_widget(label)
            except:
                pass
            self.flash_label.set_alignment(0.1,0.1)
            self.flash_label.set_text(self.flash_data[self.current_index][1])

        else:
            label=self.flash_frame.get_label_widget()
            label.set_text(_('word'))
            label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
            try:
                if self.flash_frame.get_label.widget()!=NULL:
                    self.flash_frame.set_label_widget(label)
            except:
                pass
            self.flash_label.set_alignment(0.5,0.5)
            self.flash_label.set_markup('<big><big><b>'+self.flash_data[self.current_index][0]+'</b></big></big>')
            
    def proceed(self):
        self.count = self.count + 1
        if self.current_index <= (self.total_count - 2):
            self.current_index = self.current_index + 1
            if self.mode == 'word':
                label = self.flash_frame.get_label_widget()
                label.set_text(_('word'))
                label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
                try:
                    if self.flash_frame.get_label_widget()!=NULL:
                        self.flash_frame.set_label_widget(label)
                except:
                    pass
                self.flash_label.set_alignment(0.5,0.5)
                self.flash_label.set_markup('<big><big><b>'+self.flash_data[self.current_index][0]+'</b></big></big>')
            elif self.mode == 'definition':
                label = self.flash_frame.get_label_widget()
                label.set_text(_('definition'))
                label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
                try:
                    if self.flash_frame.get_label_widget()!=NULL:
                        self.flash_frame.set_label_widget(label)
                except:
                    pass

                self.flash_label.set_text(self.flash_data[self.current_index][1])
                self.flash_label.set_alignment(0.1, 0.1)
                self.flash_label.set_max_width_chars(50)
                try:
                    self.flash_label.set_line_wrap()
                except:
                    pass
        elif self.current_index in range((self.total_count -2),self.total_count):
            self.current_index = self.current_index + 1
        if self.count == self.total_count:
            self.button_iknow.set_sensitive(False)
            self.button_idunno.set_sensitive(False)
            self.button_check.set_sensitive(False)
            self.flash_label.set_text('OVER!!!')

    def on_iknow_clicked(self, widget=None, event=None):
        #print self.current_index
        if self.current_index <= (self.total_count - 1):
            self.correct_no = self.correct_no + 1
            self.correct_label.set_text(str(self.correct_no))
            self.correct.append(self.flash_data[self.current_index])
            self.proceed()

    def on_idunno_clicked(self, widget=None, event=None):
        if self.current_index <= self.total_count - 1:
            self.incorrect_no = self.incorrect_no + 1
            self.incorrect_label.set_text(str(self.incorrect_no))
            self.incorrect.append(self.flash_data[self.current_index])
            self.proceed()

    def on_window_destroy(self, widget=None, event=None):
        self.dialog.destroy()
        #gtk.main_quit()
    def on_flash_window_destroy(self, widget=None, event=None):
        gtk.main_quit()

    def on_entry1_changed(self, widget=None, event=None):
        str_count = self.entry1.get_text()
        if str_count.isdigit():
            self.count_ = int(str_count)
            if self.count_ > len(self.get_accuracy_table()):
                self.count_ = len(self.get_accuracy_table())
            self.dialog_proceed.set_sensitive(True)
        else:
            self.dialog_proceed.set_sensitive(False)
    def on_dialog_choice_toggled(self, widget=None, event=None):
        for i in [self.choice1, self.choice2, self.choice3, self.choice4]:
            if i.get_active():
                choice = i.get_child().get_text()
        if choice != 'Custom':
            self.dialog_proceed.set_sensitive(True)
            count = int(choice)
            self.entry1.set_editable(False)
            self.entry1.set_sensitive(False)
            self.count_ = count
        else:
            self.entry1.set_visible(True)
            self.entry1.set_sensitive(True)
            self.entry1.set_property('is-focus', True)
            if not self.entry1.get_text().isdigit():
                self.dialog_proceed.set_sensitive(False)
            else:
                self.dialog_proceed.set_sensitive(True)
                self.count_ = int(self.entry1.get_text())
                if self.count_ > len(self.get_accuracy_table()):
                    self.count_ = len(self.get_accuracy_table())
            self.entry1.set_editable(True)
        
                
    def on_dialog_proceed_clicked(self, widget=None, event=None):
        self.no_of_ques = self.count_
        self.dialog.hide()
        self.set_up_mcq()
        self.builder.get_object('window3').show()
        
    def on_dialog_destroy(self, widget=None, event=None):
        self.dialog.destroy()
        gtk.main_quit()
        
    def show_question_num_dialog(self):
        self.dialog_proceed = self.builder.get_object('choice_button')
        self.dialog = self.builder.get_object('dialog1')
        self.choice1 = self.builder.get_object('choice1')
        self.choice2 = self.builder.get_object('choice2')
        self.choice3 = self.builder.get_object('choice3')
        self.choice4 = self.builder.get_object('choice4')
        self.entry1 = self.builder.get_object('entry1')
        accuracy = self.get_accuracy_table()
        eventbox2 = self.builder.get_object('eventbox2')
        eventbox2.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#444444"))
        vbox = self.builder.get_object('vbox10')
        count = len(accuracy)
        if count <10:
            self.no_of_ques = count
            self.set_up_mcq()
            self.builder.get_object('window3').show()
        elif count >= 10 and count < 20:
            self.count_ = 10
            self.choice1.set_visible(True)
            label = self.choice1.get_child()
            label.set_markup('<span foreground="white">10</span>')
            
            self.choice2.set_visible(True)
            label = self.choice2.get_child()
            label.set_markup('<span foreground="white">'+str(count)+'</span>')

            vbox.remove(self.choice3)
            
            self.choice4.set_visible(True)
            label = self.choice4.get_child()
            label.set_markup('<span foreground="white">Custom</span>')

            self.entry1.set_visible(False)
            self.dialog.show()
        elif 20<=count<30:
            self.count_ = 10
            self.choice1.set_visible(True)
            label = self.choice1.get_child()
            label.set_markup('<span foreground="white">10</span>')

            self.choice2.set_visible(True)
            label = self.choice2.get_child()
            label.set_markup('<span foreground="white">20</span>')

            self.choice3.set_visible(True)
            label = self.choice3.get_child()
            label.set_markup('<span foreground="white">'+str(count)+'</span>')

            self.choice4.set_visible(True)
            label = self.choice4.get_child()
            label.set_markup('<span foreground="white">Custom</span>')
            self.entry1.set_visible(False)
            self.dialog.show()
        else:
            self.count_ = 10
            self.choice1.set_visible(True)
            label = self.choice1.get_child()
            label.set_markup('<span foreground="white">10</span>')

            self.choice2.set_visible(True)
            label = self.choice2.get_child()
            label.set_markup('<span foreground="white">20</span>')

            self.choice3.set_visible(True)
            label = self.choice3.get_child()
            label.set_markup('<span foreground="white">30</span>')

            self.choice4.set_visible(True)
            label = self.choice4.get_child()
            label.set_markup('<span foreground="white">Custom</span>')
            self.entry1.set_visible(False)
            self.dialog.show()
        
            
def flash():
    global db
    db = wordgroupz.wordGroupzSql()
    g = games_GUI()
    l = len(g.get_accuracy_table())
    print l
    if l ==0:
        show_sorry_dialog()
    else:
        g.builder.get_object('window2').show()
        g.builder.get_object('window2').set_icon_from_file("/usr/share/pixmaps/wordgroupz.png")
    #wordgroupz.win.window.hide()
    gtk.main()

def show_sorry_dialog():
    window = gtk.Window()
    window.set_title('Oops!')
    window.set_icon_from_file("/usr/share/pixmaps/wordgroupz.png")
    window.set_default_size(300,200)
    vbox = gtk.VBox()
    window.add(vbox)
    event = gtk.EventBox()
    vbox.pack_start(event)
    event.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#444444"))
    label = gtk.Label('Not enough data!')
    event.add(label)
    label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
    window.show_all()
    window.connect('destroy', gtk.main_quit)

def mcq():
    global db
    db = wordgroupz.wordGroupzSql()
    g = games_GUI()
    l = len(g.get_accuracy_table())
    if l <4:
        show_sorry_dialog()
    else:
        g.show_question_num_dialog()
        #g.set_up_mcq()
        #g.builder.get_object('window3').show()
        g.builder.get_object('window3').set_icon_from_file("/usr/share/pixmaps/wordgroupz.png")
    gtk.main()
    
if __name__ == '__main__':
    db = wordgroupz.wordGroupzSql()
    g = games_GUI()
    #g.window.show()
    g.builder.get_object('window3').show()
    gtk.main()
