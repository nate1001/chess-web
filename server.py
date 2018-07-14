
import random
import time
import sys
import os
import urllib

#package
from sanic import Sanic
from sanic.response import json
from sanic import response

from jinja2 import Template
from jinja2 import Environment, FileSystemLoader, select_autoescape

import chess
import chess.svg

from sqlalchemy.sql import func

#local
from model import Query
from model import Game

from model import KmodeAgg
from model import Kmode
from model import Session
from model import EcoName
from model import OpeningVar3Agg
from model import PclassEcoName
from model import PclassEcoVar1
from model import GameState

ROOT = '/home/lukehand/src/chess/web/'

loader=FileSystemLoader(ROOT + 'views/')
env = Environment(
    loader=loader,
    autoescape=select_autoescape(['html', 'xml'])
)
#env.compile_templates(ROOT + '__pycache__/cache.tmp')

def timeit(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        sys.stderr.write('func:%r args:[%r, %r] took: %2.4f sec\n' % \
          (f.__name__, args, kw, te-ts))
        return result

    return timed

@timeit
def time_render(temp, *args, **kwargs):
    return temp.render(*args, **kwargs)

def randomize():
    return '?' + str(random.randint(1, 1000000))
def fmt_ps(pieces, squares):
    l = []
    for p, s in zip(pieces, squares):
        l.append("{}{}".format(p, chess.SQUARE_NAMES[s]))
    return '{' + ','.join(l) + '}'
from markupsafe import Markup

def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return Markup(s)


env.globals['randomize'] = randomize
env.globals['fmt_ps'] = fmt_ps
env.globals['urlencode'] = urlencode_filter

app = Sanic()
app.static('/s/', './static')
app.static('/img/', './static/img')
app.static('/svg/', './static/svg')
app.static('/js/', './static/js')
app.static('/favicon.ico', './static/img/favicon.ico')
app.static('/scipy/', '../scipy/img/')


def _no_results():
    t = env.get_template("no_results.jinja")
    return response.html(t.render())

@app.middleware('request')
async def add_start_time(request):
    request['start_time'] = time.time()


@app.middleware('response')
async def add_spent_time(request, response):
    spend_time = round((time.time() - request['start_time']) * 1000)
    sys.stderr.write("timing: {} {} {} {} {}ms\n".format(response.status, request.method,
                                           request.path, request.query_string, spend_time))

@app.route("/")
async def index(request):
    t = env.get_template("index.jinja")
    return response.html(t.render())

@app.route("/openings")
async def openings(request):

    session = Session()
    openings = session.query(EcoName)
    t = env.get_template("openings.jinja")
    return response.html(t.render(eco=openings))

@app.route("/openings/<name>")
async def openings_name(request, name):

    name = urllib.parse.unquote(name)
    session = Session()
    rows = session.query(OpeningVar3Agg).filter_by(name=name)
    if not rows.count():
        return _no_results()
    names = sorted(set([row.var1 for row in rows if row.var1]))

    t = env.get_template("openings_name.jinja")
    return response.html(t.render(name=name, rows=rows, names=names))

@app.route("/opening/var/<id>")
async def opening_var(request, id):

    session = Session()
    opening = session.query(OpeningVar3Agg).filter_by(openingid=id).first()
    if not opening:
        return _no_results()

    games = session.query(GameState).filter_by(openingid=id).\
        order_by(func.random()).limit(50)

    t = env.get_template("opening_var.jinja")
    return response.html(t.render(opening=opening, games=games))

@app.route("/pawns")
async def pawns(request):
    rows = Session().query(KmodeAgg)
    t = env.get_template("pawns.jinja")
    return response.html(time_render(t, rows=rows))

@app.route("/pawns/<id>")
async def pawns_id(request, id):

    session = Session()
    pawns = session.query(KmodeAgg).filter_by(pclass=id)
    if not pawns.count():
        return _no_results()

    eco = session.query(PclassEcoName).filter_by(pclass=id)
    var1 = session.query(PclassEcoVar1).filter_by(pclass=id)

    rows = session.query(Kmode).filter_by(pclass=id).\
        order_by(func.random()).limit(20)
    t = env.get_template("pawns_id.jinja")

    return response.html(t.render(rows=rows, pawn=pawns[0], eco=eco, var1=var1))

@app.route("/game")
async def game(request):

    g = Query.random_game()
    game = Game.get(g.site)

    if not game:
        t = env.get_template("no_results.jinja")
        return response.html(t.render())
    else:
        t = env.get_template("game.jinja")
        return response.html(t.render(game=game))




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
