#!/usr/bin/env python

'''
This python file will get the various fields from
a text file of a wiki page that has been produced
by html2text.py
'''
import re

class get_wiki_data:
    def __init__(self, filename):
        self.f = open(filename, 'r')
        #self.s = filename
        self.s = self.f.read()
        self.sections = self.s.split('\n## ')
        self.pos = ['Noun', 'Verb', 'Pronoun', 'Adjective', 'Adverb', 'Preposition', 'Conjunction', 'Interjection', 'Antonyms', 'Synonyms', 'Derived terms']

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
                        
        print self.fields

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
                    i = i.split('\n')
                    for j in i:
                        if j.startswith('!'):
                            i.remove(j)
                    i = '\n'.join(i)
                    self.dict[key][index] = i

        for i in self.dict[u'Derived terms']:
            index = self.dict[u'Derived terms'].index(i)
            i = i.replace('\n\n', '\n')
            self.dict[u'Derived terms'][index] = i
            
            #print self.dict[key]

    def show(self, key):
        if key in self.dict.keys():
            print key+':'
            count = 1
            for i in self.dict[key]:
                print '\t'+ str(count)+'. '+i
                count = count + 1
    def get_field_details(self):
        self.dict = {}
        
        for i in self.sections:
            if i.split('\n')[0].endswith('English'):
                self.eng_sec = i
        #print self.eng_sec
        self.eng_secs = self.eng_sec.split('\n###')
        #print self.eng_secs
        count = 0
        for i in self.eng_secs:
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
            elif t[0].split('] ')[-1] in self.pos:
                title = t[0].split('] ')[-1]
                if title not in self.dict.keys():
                    self.dict[title] = ['\n'.join(t[1:-1])]
                else:
                    self.dict[title].append('\n'.join(t[1:-1]))
                
        self.cleanup()
        #self.show('Etymology')
        #print self.dict.keys()

    #def cleanup(self):
    def save_str(self):
        s = ''
        for i in self.fields[1:-1]:
            if len(i[0]) == 3:
                for key in self.dict.keys():
                    if i[1] == key:
                        s = s + '#' + i[1]
                        self.dict[key][0] = self.dict[key][0].split('\n')
                        for i in self.dict[key][0]:
                            line = i
                            line = line.replace('*', '')
                            line = line.replace('_', '')
                            line = line.strip()
                            self.dict[key][0][self.dict[key][0].index(i)] = line
                        self.dict[key][0] = '\n'.join(self.dict[key][0])
                        s = s + '\n' + self.dict[key][0] + '\n'
                    elif i[1].find(key)>=0:
                        s = s + '#' + i[1]
                        #self.dict[key][0]
                        self.dict[key][0] = self.dict[key][0].split('\n')
                        for i in self.dict[key][0]:
                            line = i
                            line = line.replace('*', '')
                            line = line.replace('_', '')
                            line = line.strip()
                            self.dict[key][0][self.dict[key][0].index(i)] = line
                        self.dict[key][0] = '\n'.join(self.dict[key][0])
                        s = s + '\n' + self.dict[key][0] + '\n'
                        self.dict[key].remove(self.dict[key][0])
            elif len(i[0]) == 5:
                for key in self.dict.keys():
                    if i[1] == key:
                        if len(self.dict[key]) > 0:
                            s = s + '\t#' + key
                            self.dict[key][0] = self.dict[key][0].split('\n')
                            for i in self.dict[key][0]:
                                line = i
                                line = line.replace('*', '')
                                line = line.replace('_', '')
                                line = line.strip()
                                line = '\t'+line
                                self.dict[key][0][self.dict[key][0].index(i)] = line
                            self.dict[key][0] = '\n'.join(self.dict[key][0])
                            s = s + '\n' + self.dict[key][0] + '\n'
                            self.dict[key].remove(self.dict[key][0])

            elif len(i[0]) == 7:
                for key in self.dict.keys():
                    if i[1] == key:
                        if len(self.dict[key]) > 0:
                            s = s + '\t\t#' + key
                            self.dict[key][0] = self.dict[key][0].split('\n')
                            for i in self.dict[key][0]:
                                line = i
                                line = line.replace('*', '')
                                line = line.replace('_', '')
                                line = line.strip()
                                line = '\t\t'+line
                                self.dict[key][0][self.dict[key][0].index(i)] = line
                            self.dict[key][0] = '\n'.join(self.dict[key][0])
                            s = s + '\n' + self.dict[key][0] + '\n'
                            self.dict[key].remove(self.dict[key][0])
                
        return s
def main(txt_html):
    g = get_wiki_data(txt_html)
    g.get_contents()
    g.get_eng_fields()
    g.get_field_details()
    data = g.save_str()
    return data


if __name__ == '__main__':
    g = get_wiki_data('tmp.bak')
    g.get_contents()
    g.get_eng_fields()
    g.get_field_details()
    g.save_str()







    
