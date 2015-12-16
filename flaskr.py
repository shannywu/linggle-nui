# all the imports
from __future__ import with_statement
from contextlib import closing
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import linggleit as linggle
from contextlib import closing

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

inq = ['']
res = []
@app.route('/')
def show_result():
    return render_template('show_result.html', output=res, inputquery=inq) #,addentry=addentry)

@app.route('/add', methods=['POST'])
def add_entry():
    inq[0] = request.form['text'] # input text
    if inq[0]:
        res = linggle.transQuery(inq[0])
        #colType = res[0]
        #res = res[1:]
        #print colType
        return render_template('show_result.html', output=res, inputquery=inq) #,addentry=addentry)
    return redirect(url_for('show_result'))

if __name__ == '__main__':
    app.run()