
import random

#package
from sanic import Sanic
from sanic.response import json
from sanic import response

from jinja2 import Template
from jinja2 import Environment, FileSystemLoader, select_autoescape

import chess
import chess.svg

#local
import svgboard
from svgboard import SvgBoard
from heatmap import Heatmap
import db

ROOT = '/home/lukehand/src/chess/web/'
env = Environment(
    loader=FileSystemLoader(ROOT + 'views/'),
    autoescape=select_autoescape(['html', 'xml'])
)
heatmapgen = Heatmap()

def randomize():
    return '?' + str(random.randint(1, 1000000))

def svg(pos, id=None, keysquares=None, size=400):

    svg = SvgBoard(size=size, labels=False)
    for score, square, piece in zip(pos.scores, pos.squares, pos.pieces):
        svg.add_piece(square, piece)
        if square in pos.keysquares:
            if hasattr(pos, 'querysquares') and square in pos.querysquares:
                print(44, pos.querysquares)
                svg.add_circle(square, stroke='green')
            else:
                svg.add_circle(square)

        color = heatmapgen.color(score)
        if color:
            svg.set_square_color(square, color)
    svg.add_legend()
    if not hasattr(pos, 'distance'):
        pos.distance=None
    svg.add_title("{} {} {} {}".format(pos.side, pos.distance, round(pos.score*.01, 2), pos.site))
    svg.add_caption("{}".format(pos.board.fen()))
    #svg.add_arrow(0, 16)
    #svg.add_title("HELLO", 'http://example.com')
    #svg.add_caption("bye")
    return svg.tostring()


def fmt_ps(pieces, squares):
    l = []
    for p, s in zip(pieces, squares):
        l.append("{}{}".format(p, chess.SQUARE_NAMES[s]))
    return '{' + ','.join(l) + '}'

env.globals['randomize'] = randomize
env.globals['svg'] = svg
env.globals['fmt_ps'] = fmt_ps

app = Sanic()
app.static('/s/', './static')
app.static('/img/', './static/img')
app.static('/svg/', './static/svg')

@app.route("/")
async def test(request):

    pos = db.Query.random_position()
    t = env.get_template("single.jinja")
    return response.html(t.render(pos=pos))

@app.route("/test")
async def test(request):
    svg = svgboard.basic_shapes().tostring()
    t = env.get_template("test.jinja")
    return response.html(t.render(svg=svg))

@app.route("/search")
async def search(request):
    l = []
    for i, row in enumerate(db.Query.random_search()):
        row.id = i
        l.append(row)

    query = db.Query.select_fen(l[0].queryboard.fen())

    t = env.get_template("index.jinja")
    return response.html(t.render(query=query, results=l))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
