from sanic import Sanic
from sanic.response import json
from sanic import response

from jinja2 import Template
from jinja2 import Environment, FileSystemLoader, select_autoescape

import db

ROOT = '/home/lukehand/src/chess/web/sanic/'

env = Environment(
    loader=FileSystemLoader(ROOT + 'views/'),
    autoescape=select_autoescape(['html', 'xml'])
)

import random
def randomize():
    return '?' + str(random.randint(1, 1000000))

env.globals['randomize'] = randomize

app = Sanic()
app.static('/s/', './static')
app.static('/img/', './static/img')

@app.route("/")
async def test(request):
    n, results = db.Query.random_search()

    l = []
    for row in results:
        l.append(row)
    query = l[0]['query']

    t = env.get_template("index.jinja")
    return response.html(t.render(query=query, results=l))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
