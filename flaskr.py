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
#@app.before_request
# def connect_db():
#     return sqlite3.connect(app.config['DATABASE'])

# def init_db():
#     with closing(connect_db()) as db:
#         with app.open_resource('schema.sql', mode='r') as f:
#             db.cursor().executescript(f.read())
#         db.commit()

# @app.before_request
# def before_request():
#     g.db = connect_db()

# @app.after_request
# def after_request(response):
#     g.db.close()
#     return response

@app.route('/')
def show_result():
    return render_template('show_result.html', output=res, inputquery=inq) #,addentry=addentry)

@app.route('/add', methods=['POST'])
def add_entry():
    inq[0] = request.form['text'] # input text
    
    # while len(new_chars) != 0: 
    #     del new_chars[len(new_chars)-1]
    if inq[0] != '':
        #linggle.init()
        res = linggle.transQuery(inq[0])
        print res
        #     new_chars.append((c,chr(ord(c)-1),chr(ord(c)+1)))
        return render_template('show_result.html', output=res, inputquery=inq) #,addentry=addentry)
    return redirect(url_for('show_result'))

if __name__ == '__main__':
    app.run()