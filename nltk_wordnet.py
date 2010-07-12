#!/usr/bin/env python

import sys
from nltk.corpus import wordnet

def get_definition(word):
    synsets = wordnet.synsets(word)
    s = "from offline_wordnet: "
    s = s + '\n' + word
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
