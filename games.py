#!/usr/bin/evn python
# games.py
import pygtk
import gtk
import wordgroupz

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
        self.count = len(self.flash_data)
        #self.check.connect('clicked', self.on_check_clicked)
        self.correct = []
        self.incorrect = []
        self.correct_no = 0
        self.incorrect_no = 0

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
        if self.current_index < (self.count - 2):
            self.current_index = self.current_index + 1
            self.flash_frame.set_label('word')
            self.flash_label.set_text(self.flash_data[self.current_index][0])

    def on_iknow_clicked(self, widget=None, event=None):
        self.correct_no = self.correct_no + 1
        self.correct.append(self.flash_data[self.current_index])
        self.proceed()

    def on_idunno_clicked(self, widget=None, event=None):
        self.incorrect_no = self.incorrect_no + 1
        self.incorrect.append(self.flash_data[self.current_index])
        self.proceed()

if __name__ == '__main__':
    db = wordgroupz.wordGroupzSql()
    g = games_GUI()
    g.window.show()
    gtk.main()