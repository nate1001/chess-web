from sanic import Sanic
from sanic.response import json
from sanic import response

from jinja2 import Template
from jinja2 import Environment, FileSystemLoader, select_autoescape

import chess
import chess.svg

import db
ROOT = '/home/lukehand/src/chess/web/'

env = Environment(
    loader=FileSystemLoader(ROOT + 'views/'),
    autoescape=select_autoescape(['html', 'xml'])
)

import random
def randomize():
    return '?' + str(random.randint(1, 1000000))

def svg(pos, id=None, keysquares=None, size=400):
    return pos.svg(id=pos.id, size=size)

def svg_fen(board, querykey=[], size=400, **kwargs):

    circles = []
    for square in querykey:
        circles.append((square, square))

    txt = chess.svg.board(board, arrows=circles, size=size, **kwargs)
    return txt

def fmt_ps(pieces, squares):
    l = []
    for p, s in zip(pieces, squares):
        l.append("{}{}".format(p, chess.SQUARE_NAMES[s]))
    return '{' + ','.join(l) + '}'

env.globals['randomize'] = randomize
env.globals['svg'] = svg
env.globals['svg_fen'] = svg_fen
env.globals['fmt_ps'] = fmt_ps

app = Sanic()
app.static('/s/', './static')
app.static('/img/', './static/img')

@app.route("/")
async def test(request):

    pos = db.Query.random_position()
    t = env.get_template("single.jinja")
    return response.html(t.render(pos=pos))

@app.route("/search")
async def search(request):
    l = []
    for i, row in enumerate(db.Query.random_search()):
        row.id = i
        l.append(row)
    query = l[0].queryboard
    querytxt = l[0].querykey

    querykey = []
    print(44, l[0].querykey)
    for p in l[0].querykey[1:-1].split(","):
        querykey.append(chess.SQUARE_NAMES.index(p[1:]))

    t = env.get_template("index.jinja")
    return response.html(t.render(query=query, querykey=querykey, querytxt=querytxt, results=l))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
