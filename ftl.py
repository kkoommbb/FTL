# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os

import json
import datetime
from flask import Flask, render_template
from flask_flatpages import FlatPages, pygments_style_defs
from flask_frozen import Freezer

DEBUG = True
FLATPAGES_LESSON_AUTO_RELOAD = DEBUG
FLATPAGES_LESSON_EXTENSION = '.md'
FLATPAGES_LESSON_ROOT = os.path.join('content', 'lessons') 
FLATPAGES_INFO_MARKDOWN_EXTENSIONS=['codehilite','mdx_katex']


FLATPAGES_INFO_AUTO_RELOAD = DEBUG
FLATPAGES_INFO_EXTENSION = '.md'
# FLATPAGES_INFO_ROOT = 'content'
FLATPAGES_INFO_ROOT = os.path.join('content', 'info')  

FLATPAGES_INFO_MARKDOWN_EXTENSIONS=['codehilite','mdx_katex']


app = Flask(__name__)
lessonpages = FlatPages(app, name="lesson")
infopages = FlatPages(app, name="info")
freezer = Freezer(app)
app.config.from_object(__name__)

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
                    '11A': sortlessons(works(lessonpages, work='class', grade='11A'), works(lessonpages, work='home', grade='11A')), 
                    '11B': sortlessons(works(lessonpages, work='class', grade='11B'), works(lessonpages, work='home', grade='11B'))
                },
                curdate=curdate
            )


@app.route('/pages/<path:path>')
def info(path):
    page = infopages.get_or_404(path)
    return render_template('infopage.html', page=page)



if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(host='0.0.0.0', debug=True)