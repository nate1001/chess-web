
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


from peewee import fn

#local
from model import *

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

def game_link(row):
    return '<a class="game_link" href="/game/{}">{}</a>'.format(
            row.gameid, row.gameid)

def lichess_link(row, text):
    return '<a href="http://lichess.org/{}">{}</a>'.format(
            row.gameid, text)

def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return Markup(s)


env.globals['lichess_link'] = lichess_link
env.globals['game_link'] = game_link
env.globals['randomize'] = randomize
env.globals['fmt_ps'] = fmt_ps
env.globals['urlencode'] = urlencode_filter

app = Sanic()
app.static('/s/', './static')
app.static('/img/', './static/img')
app.static('/svg/', './static/svg')
app.static('/js/', './static/js')
app.static('/brython/', './static/brython')
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

@app.route("/test")
async def test(request):

    games = Game.select().limit(1)
    positions = Position.select().where(Position.gameid==games[0].gameid)
    t = env.get_template("test.jinja")
    fens = [p.fen.fen() for p in positions]

    return response.html(t.render(fens=fens))

@app.route("/openings")
async def openings(request):

    openings = EcoName.select()
    t = env.get_template("openings.jinja")
    return response.html(t.render(eco=openings))

@app.route("/openings/<name>")
async def openings_name(request, name):

    name = urllib.parse.unquote(name)
    rows = OpeningVar3Agg.select().where(OpeningVar3Agg.name==name)
    if not rows.count():
        return _no_results()
    names = sorted(set([row.var1 for row in list(rows) if row.var1]))

    t = env.get_template("openings_name.jinja")
    return response.html(t.render(name=name, rows=rows, names=names))

@app.route("/opening/var/<id>")
async def opening_var(request, id):

    opening = OpeningVar3Agg.select().where(OpeningVar3Agg.openingid==id).first()
    if not opening:
        return _no_results()

    games = GameState.select().where(GameState.openingid==id).\
        order_by(fn.random()).limit(50)

    t = env.get_template("opening_var.jinja")
    return response.html(t.render(opening=opening, games=games))

async def _kmode(request, kmode, title, folder):
    rows = kmode.select().order_by(kmode.count.desc())

    t = env.get_template("kmode.jinja")

    return response.html(time_render(t, rows=rows, title=title, folder=folder))


def _kmode_id(request, id, kmode, kmodeagg, eco_name, eco_var1, title):

    k = kmodeagg.select().where(kmodeagg.kclass==id).first()
    if not kmode:
        return _no_results()

    eco = eco_name.select().where(eco_name.kclass==id)
    var1 = eco_var1.select().where(eco_var1.kclass==id)

    games = kmode.select().where(kmode.kclass==id).\
        order_by(fn.random()).limit(20)

    t = env.get_template('kmode_id.jinja')
    return response.html(t.render(kmode=k, eco=eco, var1=var1,
        games=games,
        title=title))

@app.route("/pawns")
def pawns(request):

    return _kmode(request, KModeAggPawn, 'Canonical Pawn Formations', 'pawns')

@app.route("/pawns/<id>")
async def pawns_id(request, id):

    return _kmode_id(
            request, id, 
            KModePawn, KModeAggPawn, 
            KclassEcoNamePawn,
            KclassEcoVar1Pawn,
            'Pawn Formations')

@app.route("/mg")
def mg(request):
    return _kmode(request, KModeAggWmg, 'White Middle Game Systems', 'mg')

@app.route("/mg/<id>")
async def mg_id(request, id):

    return _kmode_id(
            request, id, 
            KModeWmg, KModeAggWmg, 
            KclassEcoNameWmg,
            KclassEcoVar1Wmg,
            'White Middle Game Systems')

@app.route("/game/<id>")
async def game(request, id):

    game = Game.get(Game.gameid==id)
    if not game:
        return _no_results()
    positions = Position.select().where(Position.gameid==id)
    fens = [p.fen.fen() for p in positions]
    gamestate = GameState.get(GameState.gameid==id)
    opening = OpeningVar3Agg.get(OpeningVar3Agg.openingid==game.openingid)
    pawn = KModePawn.get(KModePawn.gameid==game.gameid)
    wmg = KModeWmg.get(KModeWmg.gameid==game.gameid)
    bmg = KModeBmg.get(KModeBmg.gameid==game.gameid)

    t = env.get_template("game_id.jinja")
    return response.html(t.render(
        game=game,
        fens=fens,
        gamestate=gamestate,
        opening=opening,
        pawn=pawn,
        wmg=wmg,
        bmg=bmg,
        ))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
