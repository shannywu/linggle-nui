import fileinput
import sqlite3

TABLE_SCHEMA = ('CREATE TABLE WordLemma('
                    "word TEXT, "
                    'lemma TEXT, '
                    'tag TEXT, '
                    'probability REAL, '
                    'PRIMARY KEY (word, lemma, tag)'
                    ');')

def get_connection():
    conn = sqlite3.connect('bnc_word_lemma.db')
    conn.text_factory = str
    return conn

def parse_bnc_word_lemma():
    for line in fileinput.input('bnc.word.lemma.pos.txt'):
        lemma, word, tag, count, total, prob = line.split()
        # data parsing
        lemma, word, tag, count, total, prob = lemma[1:-1], word[1:-1], tag[1:-1], float(count), float(total), float(prob)
        # ignore foreign word (tag = F)
        if tag == 'F': continue
        yield (word, lemma, tag, prob)

def init_word_lemma_db(word_lemmas):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS WordLemma;")
        # create table
        cur.execute(TABLE_SCHEMA)
        # insert data
        cur.executemany('INSERT INTO WordLemma VALUES (?,?,?,?)', word_lemmas)

def search_lemma(word):
    with get_connection() as conn:
        cur = conn.cursor()
        cmd = 'SELECT lemma, MAX(probability) FROM WordLemma WHERE word="%s";' % (word)
        for res in cur.execute(cmd):
            return res[0]

def search_tag(word):
    with get_connection() as conn:
        cur = conn.cursor()
        cmd = 'SELECT lemma, tag FROM WordLemma WHERE word="%s";' % (word)
        return [res[1] for res in cur.execute(cmd)]

if __name__ == '__main__':
    # bnc word lemma data
    word_lemmas = list(parse_bnc_word_lemma())
    # insert data into sqlite3 db
    init_word_lemma_db(word_lemmas)
    # search example. (Notice: result will be None if not exist)
    print search_lemma('beach');