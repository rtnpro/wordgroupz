#!/bin/env python
import sys
import os
import subprocess

class espeak:

    def __init__(self):
        self.cmd = {}
        self.cmd['-a'] = 250
        self.cmd['-g'] = 10
        self.cmd['-p'] = 180
        self.cmd['-s'] = 140


    def set_amplitude(self,amp):
        self.cmd['-a'] = int(amp)
    def set_word_gap(self,gap):
        self.cmd['-g'] = int(gap)
    def set_pitch(self,pitch):
        self.cmd['-p'] = int(pitch)
    def set_speed(self,speed):
        self.cmd['-s'] = int(speed)
    def set_voice(self,voice):
        self.cmd['-v'] = str(voice)
    def get_amplitude(self):
        return self.cmd['-a']
    def get_word_gap(self):
        return self.cmd['-g']
    def get_pitch(self):
        return self.cmd['-p']
    def get_speed(self):
        return self.cmd['-s']
    def get_voice(self):
        return self.cmd['-v']

    def speak(self,word):
        args = ['espeak']
        i = 0
        for k in self.cmd.keys():

            args.append(str(k) + ' ' + str(self.cmd[k]))

        args.append(word)

        subprocess.call(args)

if __name__ == "__main__":

    obj = espeak()
 #   k.speak("hello")
 #   k.speak("world")
