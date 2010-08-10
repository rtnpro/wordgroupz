#!/usr/bin/evn python
# games.py
import pygtk
import gtk
import wordgroupz
import random

class games_GUI:
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file('games.glade')
        self.builder.connect_signals(self)
        self.window = self.builder.get_object('games')
        self.flash_data = db.get_details_for_flashcard()
        self.flash_frame = self.builder.get_object('frame2')
        self.flash_label = self.builder.get_object('label13')
        self.flash_frame.set_label('word')
        self.current_index = 0
        self.flash_label.set_text(self.flash_data[self.current_index][0])
        self.check = self.builder.get_object('check')
        self.total_count = len(self.flash_data)
        self.count = 0
        self.total_count_label = self.builder.get_object('label1')
        self.correct_label = self.builder.get_object('label2')
        self.incorrect_label = self.builder.get_object('label3')
        self.total_count_label.set_text(str(self.total_count))
        self.radio_word = self.builder.get_object('byword')
        self.radio_definition = self.builder.get_object('bydefinition')
        self.check_random = self.builder.get_object('random')
        self.button_iknow = self.builder.get_object('iknow')
        self.button_idunno = self.builder.get_object('idunno')
        self.button_check = self.builder.get_object('check')
        #self.check.connect('clicked', self.on_check_clicked)
        self.correct = []
        self.incorrect = []
        self.correct_no = 0
        self.incorrect_no = 0
        self.mode='word'
        self.question = self.builder.get_object('label6')
        self.option=[]
        self.option0 = self.builder.get_object('option0')
        self.res = ''
        for i in range(1,5):
            self.option.append(self.builder.get_object('option'+str(i)))
        self.mcq_dict = self.get_mcq_data()
        #print self.mcq_dict
        self.set_up_mcq()
        
    def set_up_mcq(self):
        d = self.mcq_dict.keys()
        random.shuffle(d)
        print 'd = ',
        print d
        self.ques = {}
        for i in d:
            opts = []
            opt_keys = [i]
            a = random.choice(self.mcq_dict[i])
            a = a[1:len(a)]
            opts.append(a)
            for j in d:
                if j not in opt_keys:
                    print 'j:'
                    print j
                    a = random.choice(self.mcq_dict[j])
                    #a = a[1:len(a)]
                    opts.append(a)
                    opt_keys.append(j)
                if len(opt_keys) == 4:
                    break
            random.shuffle(opts)
            self.ques[i] = opts
        self.question.set_text(self.ques.keys()[0])
        print self.ques
        j=0
        for i in self.option:
            
            i.set_label(self.ques[self.question.get_text()][j])
            j = j+1
        self.mcq_count = 0
        self.response = []
        self.ans = []
        for i in self.ques.keys():
            for j in self.ques[i]:
                for k in self.mcq_dict[i]:
                    if k.find(j)>=0:
                        self.ans.append(j)
        self.mcq_correct = 0
        self.mcq_incorrect = 0
        
    def on_proceed_clicked(self, widget, event=None):
        #print 'Hi'
        print self.mcq_count
        print self.total_count
        print self.res
        if self.mcq_count < self.total_count - 1:
            if self.res != '':
                print 'Hello'
                print self.res
                print 'HI'
                self.response.append(self.res)
                print self.response
                if self.response[self.mcq_count]==self.ans[self.mcq_count]:
                    self.mcq_correct = self.mcq_correct + 1
                    print self.mcq_correct
                else:
                    self.mcq_incorrect = self.mcq_incorrect +1
                    print self.mcq_incorrect
                self.mcq_count = self.mcq_count + 1

                self.question.set_text(self.ques.keys()[self.mcq_count])
                j = 0
                for i in self.option:

                    i.set_label(self.ques[self.question.get_text()][j])
                    j = j+1


        elif self.mcq_count == self.count - 1:
            pass
        else:
            self.question.set_text('OVER!')
        self.option0.set_active(True)
        self.res = ''
        
    def get_mcq_data(self):
        d = {}
        for i in self.flash_data:
            l = []
            t = i[1].split('\n')
            for x in t:
                if x.startswith('\t') and not x.startswith('\tSynonyms:'):
                    l.append(x.lstrip('\t')[2:len(x.lstrip('\t'))])
            d[i[0]]=l
        return d
    def on_random_clicked(self, widget=None, event=None):
        if self.current_index < len(self.flash_data)-2:
            self.remaining = self.flash_data[self.current_index+1:len(self.flash_data)]
        if self.check_random.get_active():
            random.shuffle(self.remaining)
            self.flash_data = self.flash_data[0:self.current_index+1]+self.remaining
        else:
            self.remaining.sort()
            self.flash_data = self.flash_data[0:self.current_index+1]+self.remaining.sort()
            
    def on_opts_toggled(self, widget=None, event=None):
        for i in self.option:
            if i.get_active():
                res = i.get_label()
                print res
                self.res = res
                break
                print res
           
                
    def on_radio_toggled(self, widget=None, event=None):
        for i in [self.radio_word, self.radio_definition]:
            if i.get_active():
                #print i.get_active()
                #print i.get_label()
                self.mode = i.get_label()
                #print self.mode
        if self.mode == 'definition':
            print self.mode
            self.flash_frame.set_label('definition')
            self.flash_label.set_text(self.flash_data[self.current_index][1])
        elif self.mode == 'word':
            self.flash_frame.set_label('word')
            self.flash_label.set_text(self.flash_data[self.current_index][0])
    def on_games_destroy(self, widget=None, event=None):
        gtk.main_quit()

    def on_check_clicked(self, widget=None, event=None):
        if self.flash_frame.get_label() == 'word':
            self.flash_frame.set_label('Definition')
            self.flash_label.set_text(self.flash_data[self.current_index][1])
        else:
            self.flash_frame.set_label('word')
            self.flash_label.set_text(self.flash_data[self.current_index][0])

    def proceed(self):
        self.count = self.count + 1
        if self.current_index <= (self.total_count - 2):
            self.current_index = self.current_index + 1
            self.flash_frame.set_label('word')
            self.flash_label.set_text(self.flash_data[self.current_index][0])
        elif self.current_index in range((self.total_count -2),self.total_count):
            self.current_index = self.current_index + 1
        if self.count == self.total_count:
            self.button_iknow.set_sensitive(False)
            self.button_idunno.set_sensitive(False)
            self.button_check.set_sensitive(False)
            self.flash_label.set_text('OVER!!!')

    def on_iknow_clicked(self, widget=None, event=None):
        print self.current_index
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

if __name__ == '__main__':
    db = wordgroupz.wordGroupzSql()
    g = games_GUI()
    g.window.show()
    gtk.main()