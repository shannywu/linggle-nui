import sqlite3

conn = sqlite3.connect('bnc_lemma.sqlite')
c = conn.cursor()

# c.execute('''CREATE TABLE Lemma
# (Word TEXT, Lemma TEXT);''')


dic = dict()

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
    c.execute("INSERT INTO Lemma (Word,Lemma) \
        VALUES (?, ?)", (key, max(dic[key])[1]));