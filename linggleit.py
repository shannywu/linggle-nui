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
    #print res
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
    return resList

def adv_aCollocation(headword):
    template1 = 'adv. ?adj. %s'
    start1 = 0
    query = template1 % headword
    return postProcess(start1, query)

def vnCollocation(headword):
    template1 = 'pron. v. ?prep. ?det. %s'
    start1 = 1
    query = template1 % headword
    return postProcess(start1, query)

def vanCollocation(headword):
    template1 = 'v. ?prep. ?det. adj. %s'
    start1 = 0
    query = template1 % headword
    post = postProcess(start1, query)

    dic = defaultdict(tuple)
    for i in range(len(post)):
        dic[post[i][0].split(' ')[0]] += tuple((post[i][0], post[i][1]))
    
    mergeList = []
    mergeItems = []
    
    for key, value in dic.items():
        freq = 0
        if len(value) >= 6:
            for i in range(len(value)):
                if i%2 == 1:
                    print 'key: ' + str(key)
                    print value[i]
                    freq += int(value[i])
                    mergeItems.append(tuple((key, value[i-1], value[i])))
            mergeList.append((key + ' ?prep. ?det. adj. ' + headword, freq))
        else:
            mergeList.append(value)

    mergeList.sort(key=lambda x:x[1], reverse=True)
    return (mergeList, mergeItems)

def anCollocation(headword):
    template1 = '?adv. det./prep. adj. %s'
    start1 = 0
    query = template1 % headword
    post = postProcess(start1, query)
    # headcount = int(linggleit(headword)[0]['count'])
    # rerank = []
    # for p in post:
    #     colcount = int(linggleit(p[0].split(' ')[0])[0]['count'])
    #     mi = math.log(float(p[1])/(colcount * headcount), 10)
    #     #print p[0], mi
    #     rerank.append((p[0], p[1], mi))
    # rerank.sort(key=lambda x:x[2], reverse=True)
    # # for r in rerank:
    # #     print r
    return post

def vpCollocation(headword):
    template1 = 'pron. %s prep. ?n.'
    start1 = 1
    query = template1 % headword
    post = postProcess(start1, query)
    # combine "pay attention to detail" & "... to details"-->"pay attention to detail/details"
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

Nouns = ['words', 'word', 'nouns', 'noun', 'things', 'thing', 'something', 'example']
Verbs = ['verbs', 'verb']
Adjs = ['adjectives', 'ADJ', 'adj']
Preps = ['preposition', 'prepositions', 'prep']
wordBeforeTarget = ['describe', 'associate with', 'associates with', 'for', 'of', 'go with', 'use with', 'go for', 'use for', 'describe for', 'do for', 'do with', 'describes', 'goes with', 'uses with', 'goes for', 'uses for', 'describes for']
deleteWord = ['a', 'an', 'the', 'how', 'what', 'is', 'are', 'which', 'I', 'you', 'can', 'could', 'should', 'would', 'be', 'What', 'what', 'How', 'how', 'Which', 'which']
Synonym = ['same', 'syn', 'synonyms', 'synonym', 'alike', 'another', 'paraphase', 'replace', 'rewrite']

def transQuery(question):
    que = [ token for token in re.findall("\w+", question)]
    # [que.remove(i) for i in deleteWord if i in que]
    print que
    speech = ['N' for i in Nouns if i in que]
    speech += ['V' for i in Verbs if i in que]
    speech += ['A' for i in Adjs if i in que]
    speech += ['P' for i in Preps if i in que]
    speech += ['S' for i in Synonym if i in que]
    speech += ['W' for i in wordBeforeTarget if ' '+i+' ' in ' '+' '.join(que)]
    print speech
    
    speech_n = list(set(speech))
    print speech_n
    if 'W' in speech_n:
        headword = [' '.join(que[(que.index(i.strip().split(' ')[-1])+1):]) for i in wordBeforeTarget if ' '+i+' ' in ' '+' '.join(que)]
        if '' in headword: headword.remove('')
    else:
        headword = [' '.join(que[(que.index(i)+1):]) for i in que if i in Synonym]
    print headword

    # use search_tag() to get headword's speech
    # noun -> n ; verb -> v ; adj -> a ; adv -> r ; prep -> p ; interjection -> i ...
    tags = sqlite.search_tag(headword[0].strip())
    print tags

    finalRes = []

    if 'V' in speech_n:
        finalRes.append([headword[0], 'v. ?prep. ?det. ' + headword[0], \
            'v. ?prep. ?det. adj. ' + headword[0]])
        finalRes.append(vnCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
    elif 'S' in speech_n:
        finalRes.append([headword[0], '~'+headword[0]])
        finalRes.append(synonym(headword[0]))
    elif 'P' in speech_n:
        finalRes.append([headword[0], headword[0] + ' prep. ?n.'])
        finalRes.append(vpCollocation(headword[0]))
    elif 'A' in speech_n:
        finalRes.append([headword[0], '?adv. adj. ' + headword[0], \
            'v. ?prep. ?det. adj. ' + headword[0]])
        finalRes.append(anCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
    elif 'N' in speech_n:
        finalRes.append([headword[0], headword[0] + ' prep. ?n.', \
            'v. ?prep. ?det. '+ headword[0], \
            'v. ?prep. ?det. adj. ' + headword[0], \
            '?adv. adj. '+headword[0], \
            'adv. ?adj. '+headword[0]])
        finalRes.append(vpCollocation(headword[0]))
        finalRes.append(vnCollocation(headword[0]))
        finalRes.append(vanCollocation(headword[0]))
        finalRes.append(anCollocation(headword[0]))
        finalRes.append(adv_aCollocation(headword[0]))
    elif 'W' in speech_n:
        if 'v' in tags or 'a' in tags:
            finalRes.append([headword[0], 'adv. ?adj. '+headword[0], \
                '?adv. adj. '+headword[0], \
                'v. ?prep. ?det. adj. '+headword[0]])
            finalRes.append(adv_aCollocation(headword[0]))
            finalRes.append(anCollocation(headword[0]))
            finalRes.append(vanCollocation(headword[0]))    
        else:
            finalRes.append([headword[0], '?adv. adj. '+headword[0], \
                'v. ?prep. ?det. adj. '+headword[0]])
            finalRes.append(anCollocation(headword[0]))
            finalRes.append(vanCollocation(headword[0]))
    else:
        finalRes.append('I don\'t know what are you talking about')

    # finalRes.append(['headword', 'test1','v. ?prep. ?det. adj.' ])
    # finalRes.append([('a',1024),('b',1124),('c',223),('d',30),('e',1434),('f',513),('g',26), ('h',134), ('i', 22), ('j', 1548)])
    # #finalRes.append([('a',600),('b',51),('c',2422),('d',3423),('e',342),('f',11),('g',310)])
    # finalRes.append(vanCollocation('difficulty'))
    #print finalRes
    
    return finalRes

if __name__ == '__main__':
    #vanCollocation('difficulty')
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
