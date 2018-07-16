
from browser import document, alert, svg, console


piece_names = {
        'P':'white-pawn', 'N':'white-knight', 'B':'white-bishop', 'R':'white-rook', 'Q':'white-queen', 'K':'white-king',
        'p':'black-pawn', 'n':'black-knight', 'b':'black-bishop', 'r':'black-rook', 'q':'black-queen', 'k':'black-king',
}

def _square_offset(i):
    x, y = i%8, i//8
    return x*8, y*8

def get_piece_args(square, piece):
    name = piece_names[str(piece)]
    xc, yc = _square_offset(square)
    x, y = xc*7+4, yc*7+2,
    return (x, y, name)

fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

def set_board(g, fen):

    i = 0
    pieces = []
    ok = True

    for child in g:
        g.removeChild(child)

    for char in fen:
        #console.log('i %s char %s' % (i, char))
        if char == '/':
            continue
        if char in '12345678':
            i += int(char)
            continue
        if char == ' ':
            break
        if char.lower() not in 'pnbrqk':
            alert('fen "{}" is not correct'.format(fen))
            ok = False
            break

        x, y, name = get_piece_args(i, char)
        t = "translate({},{})".format(x, y)
        #console.log(t)
        use = svg.use(href='#' + name, transform=t)
        pieces.append(use)
        i += 1

    if ok:
        for p in pieces:
            #console.log('%s' % p)
            g.appendChild(p)

    text = svg.text(x=-24, y=69*7)
    text['class'] = 'board_fen'
    text <= fen
    g.appendChild(text)


def _move_by(inc):
    g = document['board_pieces']
    move = int(g['data-state'])
    moves = [f.strip() for f in g['data-fens'].split('\n') if f.strip()]
    if inc == float('inf'):
        i = len(moves) - 1
    elif inc == float('-inf'):
        i = 0
    else:
        i = move + inc
    if i < 0 or i > len(moves) - 1:
        return

    try:
        set_board(g, moves[i])
        g['data-state'] = i
    except IndexError:
        pass

def next_move():
    _move_by(1)
def prev_move():
    _move_by(-1)
def last_move():
    _move_by(float('inf'))
def first_move():
    _move_by(float('-inf'))


from browser import window

document["next_move"].bind("click", next_move)
window.next_move = next_move
document["prev_move"].bind("click", prev_move)
window.prev_move = prev_move
document["last_move"].bind("click", last_move)
window.last_move = last_move
document["first_move"].bind("click", first_move)
window.first_move = first_move

