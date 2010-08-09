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

    def on_random_clicked(self, widget=None, event=None):
        if self.current_index < len(self.flash_data)-2:
            self.remaining = self.flash_data[self.current_index+1:len(self.flash_data)]
        if self.check_random.get_active():
            random.shuffle(self.remaining)
            self.flash_data = self.flash_data[0:self.current_index+1]+self.remaining
        else:
            self.remaining.sort()
            self.flash_data = self.flash_data[0:self.current_index+1]+self.remaining.sort()
            
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