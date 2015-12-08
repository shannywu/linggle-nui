#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import urllib, re
from itertools import groupby, imap, product
from collections import defaultdict

def linggleit(query):
    url = 'http://linggle.com/query/{}'.format(urllib.quote(query, safe=''))
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()

dic = defaultdict(lambda: [])

def init():
    filein1 = file('bnc.word.lemma.pos.txt')
    line = filein1.readline()
    while True:
        if line == '': break
        #"be" "was" "v" 9236.00 9236.04 1.00000
        try:
            lemma, word, tag, count, _, _ = line.strip().split(' ')
            dic[word[1:-1]] += [ (int(float(count)), lemma[1:-1]) ]
        except:
            pass
        line = filein1.readline()
    for key in dic.keys():
        dic[key] = max(dic[key])[1]
    return

def postProcess(start1, query):
    print; print query; print
    res = linggleit(query)
    phrases = [ [  w.replace('<strong>','').replace('</strong>','')  for w in ngram['phrase'][start1:]] for ngram in res]
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

def vnCollocation(headword):
    template1 = 'pron. v. ?prep. ?det. %s'
    start1 = 1
    query = template1 % headword
    postProcess(start1, query)

def vanCollocation(headword):
    template1 = 'v. ?prep. ?det. adj. %s'
    start1 = 0
    query = template1 % headword
    postProcess(start1, query)

def anCollocation(headword):
    template1 = 'det./prep. adj. %s'
    start1 = 1
    query = template1 % headword
    postProcess(start1, query)

def allCollocations(headword):
    vnCollocation(headword)
    anCollocation(headword)
    vanCollocation(headword)

Nouns = ['words', 'word', 'nouns', 'noun', 'things', 'thing', 'something', 'example']
Verbs = ['verbs', 'verb']
Adjs = ['adjectives', 'ADJ', 'adj']
wordBeforeTarget = ['describe', 'for', 'go with', 'use with', 'go for', 'use for', 'describe for', 'do for', 'do with', 'describes', 'goes with', 'uses with', 'goes for', 'uses for', 'describes for']
deleteWord = ['a', 'an', 'the', 'how', 'what', 'is', 'are', 'which', 'I', 'you', 'good', 'best', 'can', 'could', 'should', 'would', 'be', 'What', 'what', 'How', 'how', 'Which', 'which', 'to']
Synonym = ['same', 'synonyms', 'synonym', 'alike', 'another']

def transQuery(question):
    que = [ token for token in re.findall("\w+", question)]
    [que.remove(i) for i in deleteWord if i in que]
    print que
    speech = ['N' for i in Nouns if i in que]
    speech += ['V' for i in Verbs if i in que]
    speech += ['A' for i in Adjs if i in que]
    speech += ['W' for i in wordBeforeTarget if i in ' '.join(que)]
    print speech
    headword = [que[que.index(i.strip().split(' ')[-1])+1] for i in wordBeforeTarget if i in ' '.join(que)]
    print headword

    if 'V' in speech:
        vnCollocation(headword[0])
        vanCollocation(headword[0])
    elif 'A' in speech:
        anCollocation(headword[0])
        vanCollocation(headword[0])
    elif 'N' in speech:
        allCollocations(headword[0])
    elif 'W' in speech:
        anCollocation(headword[0])
        vanCollocation(headword[0])
    else:
        print 'I don\'t know what are you talking about~'

def main(query):
    allCollocations(query)
    #allCollocations('role')
    return

if __name__ == '__main__':
    init()
    query = raw_input(">>query: ")
    transQuery(query)
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
