#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import urllib, re, sqlite
from itertools import groupby, imap, product
from collections import defaultdict
import fileinput

def linggleit(query):
    url = 'http://linggle.com/query/{}'.format(urllib.quote(query, safe=''))
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
'''
dic = defaultdict(lambda: [])

def init():
    for line in open('bnc.word.lemma.pos.txt'):
        print line
        #if line == '': continue

        lemma, word, tag, count, _, _ = line.strip().split(' ')
        word, lemma = word[1:-1], lemma[1:-1]
        if word in dic.keys():
            dic[word] += [ (float(count), lemma) ]
            #print dic[word]
        else:
            dic[word] = [ (float(count), lemma) ]
            #print dic[word]
            #print dic[word[1:-1]]

    for key in dic.keys():
        print dic[key]
        #print max(dic[key])[1]
        dic[key] = max(dic[key])[1]
        print dic[key]
    
    #return
'''

def postProcess(start1, query):
    #print; print query; print
    res = linggleit(query)
    phrases = [ [  w.replace('<strong>','').replace('</strong>','')  for w in ngram['phrase'][start1:]] for ngram in res]
    phrases = [ [sqlite.search_lemma(ph[0].strip().lower())]+ ph[1:] for ph in phrases]
    phrases = [ ' '.join([x.strip() for x in ph]) for ph in phrases]
    counts = [ ngram['count_str'] for ngram in res]
    counts = [ int(x.replace(',','')) for x in counts]

    ngramCounts = zip(phrases, counts)
    ngramCounts.sort(key=lambda x: x[0])
    ngramCounts = [ (ngram, sum( [x[1] for x in ngramcounts ] )) \
                    for ngram, ngramcounts in groupby(ngramCounts, key=lambda x:x[0]) ]
    ngramCounts.sort(key=lambda x:x[1], reverse=True)

    resList = []
    for ngram, count in ngramCounts:
        #print '%s\t%s' % (ngram, count)
        resList.append((ngram, count))

    #dic.clear()
    return resList

def vnCollocation(headword):
    template1 = 'pron. v. ?prep. ?det. %s'
    start1 = 1
    query = template1 % headword
    return postProcess(start1, query)

def vanCollocation(headword):
    template1 = 'v. ?prep. ?det. adj. %s'
    start1 = 0
    query = template1 % headword
    return postProcess(start1, query)

def anCollocation(headword):
    template1 = 'det./prep. adj. %s'
    start1 = 1
    query = template1 % headword
    return postProcess(start1, query)

def vpCollocation(headword):
    template1 = 'pron. %s ?prep. ?n.'
    start1 = 1
    query = template1 % headword
    return postProcess(start1, query)

def allCollocations(headword):
    vnCollocation(headword)
    anCollocation(headword)
    vanCollocation(headword)
    vpCollocation(headword)

Nouns = ['words', 'word', 'nouns', 'noun', 'things', 'thing', 'something', 'example']
Verbs = ['verbs', 'verb']
Adjs = ['adjectives', 'ADJ', 'adj']
Preps = ['preposition', 'prepositions', 'prep', 'prep.']
wordBeforeTarget = ['describe', 'associate with', 'associates with', 'for', 'go with', 'use with', 'go for', 'use for', 'describe for', 'do for', 'do with', 'describes', 'goes with', 'uses with', 'goes for', 'uses for', 'describes for']
deleteWord = ['a', 'an', 'the', 'how', 'what', 'is', 'are', 'which', 'I', 'you', 'good', 'best', 'can', 'could', 'should', 'would', 'be', 'What', 'what', 'How', 'how', 'Which', 'which', 'to']
Synonym = ['same', 'synonyms', 'synonym', 'alike', 'another']

def transQuery(question):
    que = [ token for token in re.findall("\w+", question)]
    [que.remove(i) for i in deleteWord if i in que]
    #print que
    speech = ['N' for i in Nouns if i in que]
    speech += ['V' for i in Verbs if i in que]
    speech += ['A' for i in Adjs if i in que]
    speech += ['P' for i in Preps if i in que]
    speech += ['W' for i in wordBeforeTarget if i in ' '.join(que)]
    #print speech
    headword = [' '.join(que[(que.index(i.strip().split(' ')[-1])+1):]) for i in wordBeforeTarget if i in ' '.join(que)]
    #print headword

    finalRes = []

    if 'V' in speech:
        finalRes.append(vnCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
    elif 'A' in speech:
        finalRes.append(anCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
    elif 'N' in speech:
        finalRes.append(allCollocations(headword[0]))
    elif 'P' in speech:
        finalRes.append(vpCollocation(headword[0]))
    elif 'W' in speech:
        finalRes.append(anCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
    else:
        finalRes.append('I don\'t know what are you talking about')
    
    return finalRes

#def main(query):
#    allCollocations(query)
    #allCollocations('role')
#    return

if __name__ == '__main__':
    while True:
        query = raw_input(">>(type 'EX' to exit)\n>>query: ")
        if query == 'EX': break
        else: 
            for q in transQuery(query):
                for i in q:
                    print '{}\t{}'.format(i[0],i[1])
                print '========================================'
            

    # main(query)
    '''res = linggleit('~reliable')
    phrases = [ [  w.replace('<strong>','').replace('</strong>','')  for w in ngram['phrase'][:]] for ngram in res]
    phrases = [ [dic[ph[0].strip().lower()]]+ ph[1:] for ph in phrases]
    phrases = [ ' '.join([x.strip() for x in ph]) for ph in phrases]
    counts = [ ngram['count_str'] for ngram in res]
    counts = [ int(x.replace(',','')) for x in counts]

    ngramCounts = zip(phrases, counts)
    ngramCounts.sort(key=lambda x: x[0])
    ngramCounts = [ (ngram, sum( [x[1] for x in ngramcounts ] )) \
                    for ngram, ngramcounts in groupby(ngramCounts, key=lambda x:x[0]) ]
    ngramCounts.sort(key=lambda x:x[1], reverse=True)
    for ngram, count in ngramCounts:
        print '%s\t%s' % (ngram, count)
    main()'''
