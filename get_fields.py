#!/usr/bin/env python

'''
This python file will get the various fields from
a text file of a wiki page that has been produced
by html2text.py
'''
import re

class get_wiki_data:
    def __init__(self, filename):
        #self.f = open(filename, 'r')
        self.s = filename
        #self.s = self.f.read()
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
        print self.eng_secs
        count = 0
        for i in self.eng_secs:
            #count = 0
            #self.dict[' '.join(self.fields[count])] = i
            #count = count + 19
            '''
            i = i.split('[')
            print i[3]+'^s'
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
            print links
            for link in links:
                if link.strip('[').strip(']').isdigit:
                    i = i.replace(link, '')
                else:
                    i = i.replace(link, link.strip('[').strip(']'))
                    print i'''
                    
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
        

if __name__ == '__main__':
    g = get_wiki_data('tmp')
    g.get_contents()
    g.get_eng_fields()
    g.get_field_details()
