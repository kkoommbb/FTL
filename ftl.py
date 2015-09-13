# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os

import json
import datetime
from flask import Flask, render_template, url_for
from flask_flatpages import FlatPages, pygments_style_defs
from flask_frozen import Freezer

from flask.ext.babel import Babel, format_datetime, refresh


DEBUG = True
FLATPAGES_LESSON_AUTO_RELOAD = DEBUG
FLATPAGES_LESSON_EXTENSION = '.md'
FLATPAGES_LESSON_ROOT = os.path.join('content', 'lessons') 
FLATPAGES_LESSON_MARKDOWN_EXTENSIONS=['codehilite','mdx_katex']


FLATPAGES_INFO_AUTO_RELOAD = DEBUG
FLATPAGES_INFO_EXTENSION = '.md'
FLATPAGES_INFO_ROOT = os.path.join('content', 'info')  
FLATPAGES_INFO_MARKDOWN_EXTENSIONS=['codehilite','mdx_katex']

FREEZER_DESTINATION_IGNORE = ['.git*', 'CNAME']


# for gh-pages
# FREEZER_BASE_URL = 'http://localhost/FTL/'



# APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# FREEZER_DESTINATION=os.path.join(os.path.dirname(APP_ROOT), 'ftlbuild')

app = Flask(__name__)

babel = Babel(app)

app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
refresh()


@app.template_filter('datetime')
def format_datetime(value):
    return datetime.datetime.combine(value, datetime.time())


alllessonpages = FlatPages(app, name="lesson")
def lessonpages(alllessonpages):
    return (p for p in alllessonpages if 'work' in p.meta)
def newspages(alllessonpages): 
    return (p for p in alllessonpages if 'news' in p.meta)

infopages = FlatPages(app, name="info")
freezer = Freezer(app)
app.config.from_object(__name__)

toplinks = [
    {'link':'/pages/kontrol', 'title': u'Правила'},
    {'link':'/pages/quiz', 'title': u'Зачёт'},
    {'link':'/pages/latex', 'title': 'LaTeX'},
    {'link':'/pages/mmmm', 'title': u'Исследования'},
    {'link':'/pages/books', 'title': u'Книги и ссылки'}
    ]

def sortlessons(classworks, homeworks):
    i = 0
    j = 0
    C = len(classworks)
    H = len(homeworks)
    lessons = []
    while (i < C) and (j < H):
        while (i < C) and (j < H) and (classworks[i]['date'] > homeworks[j]['date']):
            lessons.append({'date': classworks[i]['date'], 'class': [classworks[i]], 'home': []})
            i = i + 1
        while (i < C) and (j < H) and (homeworks[j]['date'] > classworks[i]['date']):
            lessons.append({'date': homeworks[j]['date'], 'class': [], 'home': [homeworks[j]]})
            j = j + 1
        while (i < C) and (j < H) and (j < H) and (homeworks[j]['date'] == classworks[i]['date']):
            lessons.append({'date': homeworks[j]['date'], 'class': [classworks[i]], 'home': [homeworks[j]]})
            i = i + 1
            j = j + 1
    while (i < C) :
        lessons.append({'date': classworks[i]['date'], 'class': [classworks[i]], 'home': []})
        i = i + 1
    while (j < H) :
        lessons.append({'date': homeworks[j]['date'], 'class': [], 'home': [homeworks[j]]})
        j = j + 1
    return lessons


def works(flatpages, work, grade):
    k = [p for p in flatpages if p['work'] == work and p['grade'] == grade]
    k.sort(key=lambda item:item['date'], reverse=True)
    return k


@app.route("/")
def lessons():
    curdate = datetime.datetime.now().date()
    return render_template(
                'lessons.html', 
                lessons={
                    '11A': sortlessons(works(lessonpages(alllessonpages), work='class', grade='11A'), works(lessonpages(alllessonpages), work='home', grade='11A')), 
                    '11B': sortlessons(works(lessonpages(alllessonpages), work='class', grade='11B'), works(lessonpages(alllessonpages), work='home', grade='11B'))
                },
                curdate=curdate,
                toplinks=toplinks,
                news={
                    '11A': (p for p in newspages(alllessonpages) if p['grade']=='11A'),
                    '11B': (p for p in newspages(alllessonpages) if p['grade']=='11B'),
                }
            )


@app.route('/pages/<path:path>/')
def info(path):
    page = infopages.get_or_404(path)
    return render_template('infopage.html', page=page, toplinks=toplinks)

@freezer.register_generator
def info():
    for link in toplinks:
        yield {'path': os.path.basename(link['link'])}



if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(host='0.0.0.0', debug=True)