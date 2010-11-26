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

import sys
import wordnet
import os
#nltk_dir = os.environ['HOME']+'/nltk_data/corpora'
wordnet_dir = '/usr/share/wordnet-3.0/dict'
if os.path.exists(wordnet_dir):
    pass
else:
    print "Please install wordnet dictionary"

def get_definition(word):
    #if not os.path.exists(nltk_dir):
    #    os.makedirs(nltk_dir)
    #if os.path.exists('/usr/share/wordnet-3.0/dict') and not os.path.exists(nltk_dir+'/wordnet'):
    #    os.symlink('/usr/share/wordnet-3.0/dict',nltk_dir+'/wordnet')

    synsets = wordnet.synsets(word)
    #s = "from offline_wordnet: "
    s = ''
    p = ''
    for synset in synsets:
        pos, type_ = synset.lexname.split('.')
        definition = synset.definition
        synonyms = synset.lemma_names
        if word in synonyms:
            synonyms.remove(word)
        if synonyms != []:
            last_syn = synonyms[len(synonyms) - 1]
        examples = synset.examples
    
        if pos != p:
            s = s + '\n' + pos
            p = pos
            count = 0
        if pos == p:
            count = count + 1
            s = s + '\n\t%d. ' %(count) + definition
            if len(synonyms) > 0:
                s = s + '\n\tSynonyms: '
            for syn in synonyms:
                if syn != last_syn:
                    s = s + syn + ', '
                else:
                    s = s + syn + '.'

    return s

if __name__ == '__main__':
    details = get_definition(sys.argv[1])
    print details
