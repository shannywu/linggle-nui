#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import urllib, re, sqlite
from itertools import groupby, imap, product
from collections import defaultdict
import fileinput, math

def linggleit(query):
    url = 'http://linggle.com/query/{}'.format(urllib.quote(query, safe=''))
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()

def postProcess(start1, query):
    #print; print query; print
    res = linggleit(query)
    phrases = [ [  w.replace('<strong>','').replace('</strong>','')  for w in ngram['phrase'][start1:]] for ngram in res]
    phrases = [ [ sqlite.search_lemma(ph[0].strip().lower())]+ ph[1:] for ph in phrases]
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
    post = postProcess(start1, query)
    #print post
    # post = [(u'sandy beach', 120497), (u'private beach', 76260), \
    # (u'beautiful beach', 50240), (u'near beach', 42217), (u'good beach', 31485), \
    # (u'long beach', 27049), (u'public beach', 23965), (u'small beach', 21830), \
    # (u'nude beach', 21194), (u'main beach', 19780), (u'great beach', 14793), \
    # (u'secluded beach', 14610), (u'nice beach', 12379), (u'tropical beach', 11170), \
    # (u'nearby beach', 10881), (u'desert beach', 9812), (u'rocky beach', 8534), \
    # (u'lovely beach', 7672), (u'quiet beach', 7594), (u'local beach', 6987), \
    # (u'perfect beach', 6394), (u'spin beach', 6106), (u'popular beach', 5537), \
    # (u'concrete beach', 5263), (u'remote beach', 5056), (u'following beach', 4980), \
    # (u'famous beach', 4888), (u'ocean beach', 4837), (u'sunny beach', 4618), \
    # (u'maui beach', 4369), (u'pristine beach', 4104), (u'little beach', 4072)]

    headcount = int(linggleit(headword)[0]['count'])
    #headcount = 25866110
    #print headcount
    rerank = []
    for p in post:
        #print p[0].split(' ')[0] # first word
        colcount = int(linggleit(p[0].split(' ')[0])[0]['count'])
        mi = math.log(float(p[1])/(colcount * headcount), 10)
        print p[0], mi
        rerank.append((p[0], p[1], mi))
    rerank.sort(key=lambda x:x[2], reverse=True)
    for r in rerank:
        print r
    return rerank

def vpCollocation(headword):
    template1 = 'pron. %s ?prep. ?n.'
    start1 = 1
    query = template1 % headword
    post = postProcess(start1, query)
    tmp = []
    removeIndex = []
    for i in range(len(post)):
        lastWord = post[i][0].split(' ')[-1]
        lemma = sqlite.search_lemma(lastWord.strip().lower())
        if str(lastWord) != str(lemma):
            for j in range(len(post)):
                _lastWord = post[j][0].split(' ')[-1]
                if str(lemma) == str(_lastWord):
                    tmp.append([ post[j][0] + '/' + lastWord, int(post[j][1]) + int(post[i][1])])
                    removeIndex.append(i)
                    removeIndex.append(j)
    for ind in removeIndex:
        post.remove(post[int(ind)])
    res = tmp + post
    res.sort(key=lambda x:x[1], reverse=True)
    return res

def synonym(headword):
    query = '~'.join(headword.strip().split(' '))
    print query
    # template1 = '~%s'
    start1 = 0
    # query = template1 % headword
    return postProcess(start1, query)

# def allCollocations(headword):
#     vnCollocation(headword)
#     anCollocation(headword)
#     vanCollocation(headword)
#     vpCollocation(headword)

Nouns = ['words', 'word', 'nouns', 'noun', 'things', 'thing', 'something', 'example']
Verbs = ['verbs', 'verb']
Adjs = ['adjectives', 'ADJ', 'adj']
Preps = ['preposition', 'prepositions', 'prep']
wordBeforeTarget = ['describe', 'associate with', 'associates with', 'for', 'of', 'go with', 'use with', 'go for', 'use for', 'describe for', 'do for', 'do with', 'describes', 'goes with', 'uses with', 'goes for', 'uses for', 'describes for']
deleteWord = ['a', 'an', 'the', 'how', 'what', 'is', 'are', 'which', 'I', 'you', 'good', 'best', 'can', 'could', 'should', 'would', 'be', 'What', 'what', 'How', 'how', 'Which', 'which']
Synonym = ['same', 'syn', 'synonyms', 'synonym', 'alike', 'another', 'paraphase', 'replace', 'rewrite']

def transQuery(question):
    que = [ token for token in re.findall("\w+", question)]
    [que.remove(i) for i in deleteWord if i in que]
    # print que
    speech = ['N' for i in Nouns if i in que]
    speech += ['V' for i in Verbs if i in que]
    speech += ['A' for i in Adjs if i in que]
    speech += ['P' for i in Preps if i in que]
    speech += ['S' for i in Synonym if i in que]
    speech += ['W' for i in wordBeforeTarget if ' '+i+' ' in ' '.join(que)]
    # print speech
    speech_n = list(set(speech))
    # print speech_n
    headword = [' '.join(que[(que.index(i.strip().split(' ')[-1])+1):]) for i in wordBeforeTarget if ' '+i+' ' in ' '.join(que)]
    if '' in headword: headword.remove('')
    print headword

    finalRes = []

    if 'V' in speech_n:
        finalRes.append(['v. ?prep. ?det. ' + headword[0], \
            'v. ?prep. ?det. adj. ' + headword[0]])
        finalRes.append(vnCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
    elif 'S' in speech_n:
        finalRes.append(['~'+headword[0]])
        finalRes.append(synonym(headword[0]))
    elif 'P' in speech_n:
        finalRes.append([ headword[0] + ' ?prep. ?n.'])
        finalRes.append(vpCollocation(headword[0]))
    elif 'A' in speech_n:
        finalRes.append(['adj. ' + headword[0], \
            'v. ?prep. ?det. adj. ' + headword[0]])
        finalRes.append(anCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
    elif 'N' in speech_n:
        finalRes.append([headword[0] + ' ?prep. ?n.', \
            'v. ?prep. ?det. '+headword[0], \
            'v. ?prep. ?det. adj. ' + headword[0], \
            'adj. '+headword[0]])
        finalRes.append(vpCollocation(headword[0]))
        finalRes.append(vnCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
        finalRes.append(anCollocation(headword[0]))
    elif 'W' in speech_n:
        finalRes.append(['adj. '+headword[0], \
            'v. ?prep. ?det. adj. '+headword[0]])
        finalRes.append(anCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
    else:
        finalRes.append('I don\'t know what are you talking about')
    # finalRes.append(['test1','test2'])
    # finalRes.append([('a',0),('b',1),('c',2),('d',3),('e',4),('f',5),('g',6)])
    # finalRes.append([('a',6),('b',5),('c',4),('d',3),('e',2),('f',1),('g',0)])
    #print finalRes
    
    return finalRes

if __name__ == '__main__':
    while True:
        query = raw_input(">>(type 'EX' to exit)\n>>query: ")
        if query == 'EX': break
        else: 
            #print '0: ' + str(transQuery(query)[0])
            print '------------------------------------------------'
            for q in transQuery(query)[1:]:
                for i in q:
                    print '{}\t{}'.format(i[0],i[1])
                print '========================================'