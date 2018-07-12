
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

#local
from model import Query
from model import Game


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

@app.route("/pawns")
async def pawns(request):
    t = env.get_template("kmode.jinja")
    rows = Query.canonical_pawns()
    return response.html(time_render(t, rows=rows))

@app.route("/pawns/<id>")
async def kmode_pos(request, id):
    l = Query.kmode_positions(id)
    if not l:
        t = env.get_template("no_results.jinja")
        return response.html(t.render())
    else:
        eco = Query.eco_agg(id)
        t = env.get_template("positions.jinja")
        return response.html(time_render(t, rows=l, eco=eco))

@app.route("/search")
async def search(request):
    l = []
    for i, row in enumerate(Query.random_search()):
        l.append(row)
    if not l:
        t = env.get_template("no_results.jinja")
        return response.html(t.render())
    else:
        query = Query.select_fen(l[0].queryboard.fen())
        t = env.get_template("index.jinja")
        return response.html(t.render(query=query, results=l))

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

@app.route("/openings")
async def openings(request):

    eco = Query.openings()
    if not eco:
        return _no_results()
    else:
        t = env.get_template("openings.jinja")
        return response.html(t.render(eco=eco))

@app.route("/openings/<name>")
async def opening(request, name):

    name = urllib.parse.unquote(name)
    rows = Query.opening(name)

    d = {}
    for row in rows:
        if row.var1:
            d[row.var1] = None
    if not rows:
        return _no_results()
    else:
        t = env.get_template("opening_var2.jinja")
        return response.html(t.render(name=name, rows=rows, names=sorted(d.keys())))


@app.route("/opening/var/<id>")
async def opening_var(request, id):

    opening, games = Query.opening_var(id)

    if not opening:
        return _no_results()
    else:
        t = env.get_template("opening_var.jinja")
        return response.html(t.render(opening=opening, games=games))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
