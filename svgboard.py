#!/usr/bin/env python3
#coding:utf-8

import svgwrite
import chess
import math


def to_bb_idx(i):
    #from chess square idx, i.ie 1st quadrant math
    return (56 - (i//8)*8 + (i%8))

def to_square_idx(i):
    #from fen string idx, i.e. 4th quadrant math
    return ((i)//8)*8 + ((8 - (i)%8) - 1)

def from_bb_idx(i):
    # from cpiece board to square idx
    return ( 63 - ((i)//8)*8 - (7 - (i)%8))  



class SvgBoard:

    style = """
        .blacksquare { fill:  #f2f2f2; }
        .whitesquare { fill: #b3b3b3; }

        .blacksquare { fill:  #f5f5f5; stroke:black; stroke-width:.1px; }
        .whitesquare { fill: none; stroke:gray; stroke-width:.2px; }

        a {fill : blue }
        a:hover { cursor: pointer }

        .title{ font-size: 4px; }
        .caption{ font-size: 2px;}
        .legend{ font-size: 2px;}
        .labels text {  font-size: 2px; opacity:.5 }
        .circles { fill:none; stroke-width:1px; stroke:blue; opacity:.3; stroke-width:.5px}
        .arrows { fill:blue; stroke:blue; stroke-width:2px; opacity:.5}
        .arrowhead {fill:blue; stroke:blue; opacity:.5, stroke-widith:0; }

    """
    piece_names = {
            'P':'white-pawn', 'N':'white-knight', 'B':'white-bishop', 'R':'white-rook', 'Q':'white-queen', 'K':'white-king',
            'p':'black-pawn', 'n':'black-knight', 'b':'black-bishop', 'r':'black-rook', 'q':'black-queen', 'k':'black-king',
    }

    def _offset(self, x, y):
        return x * 8, y * 8

    def _square_offset(self, square):
        i = to_bb_idx(square)
        x, y = i%8, i//8
        return self._offset(x, y)

    def __init__(self, size=400, id=None, labels=True):

        def group(classname):
            return dwg.add(dwg.g(class_=classname))

        dwg = svgwrite.Drawing(size=(size,size))
        dwg.viewbox(0, 0, 64, 64)

        triangle = dwg.path("M2,1 L2,11 L10,6 L2,1".split(), class_='arrowhead')
        self.marker = dwg.marker(insert=(2, 6.25), size=(8, 8), orient='auto') # target size of the marker
        self.marker.viewbox(minx=-5, miny=-5, width=32, height=32) # the marker user coordinate space
        self.marker.add(triangle)
        dwg.defs.add(self.marker)

        self._squares = group("chessboard")
        self._pieces = group("pieces")
        self._pieces.scale(.143)
        self._circles= group("circles")
        self._arrows= group("arrows")
        self._title= group("title")
        self._caption = group("caption")
        self._legend = group("legend")
        self._labels = group("labels")

        self._dims = 0, 0, 64, 64

        # draw squares
        i = 0
        for y in range(8):
            for x in range(8):
                xc, yc = self._offset(x, y)
                name = chess.SQUARE_NAMES[from_bb_idx(i)]
                kind = ('whitesquare' if (x+y) % 2 else 'blacksquare')
                square = dwg.rect(class_=kind, id=name, insert=(xc, yc), size=(8, 8))
                self._squares.add(square)

                if labels:
                    label = dwg.text(name, insert=(xc+0, yc+2))
                    self._labels.add(label)
                i += 1
	
        dwg.defs.add(dwg.style(self.style))
        self.dwg = dwg


    def tostring(self):
        return self.dwg.tostring()
    
    def add_legend(self):
        of = 5
        x, y, w, h = self._dims

        x -= of
        w += of
        r,f = '87654321', 'abcdefgh'
        for i in range(8):
            xc, yc = self._offset(-1, i)
            label = self.dwg.text(r[i], insert=(-3, yc+of))
            self._legend.add(label)

        h += of
        for i in range(8):
            xc, yc = self._offset(i, 8)
            label = self.dwg.text(f[i], insert=(xc+3, yc+2))
            self._legend.add(label)

        self.dwg.viewbox(x, y, w, h)
        self._dims = x, y, w, h


    def add_title(self, txt, href=None):
        of = 5
        x, y, w, h = self._dims
        y -= of
        h += of
        self._dims = x, y, w, h
        self.dwg.viewbox(x, y, w, h)

        txt = self.dwg.text(txt, insert=(0, -1))
        if href:
            a = (self.dwg.a(href))
            a.add(txt)
            self._title.add(a)
        else:
            self._title.add(txt)

    def add_caption(self, txt):
        of = 7
        x, y, w, h = self._dims
        h += of
        self._dims = x, y, w, h
        self.dwg.viewbox(x, y, w, h)
        label = self.dwg.text(txt, insert=(0, 64+of-2))
        self._caption.add(label)

    def add_piece(self, square, piece, **kwargs):
        xc, yc = self._square_offset(square)
        name = self.piece_names[str(piece)]
        piece = self.dwg.use("#" + name)
        piece.translate(xc*7+4, yc*7+2, **kwargs)
        self._pieces.add(piece)

    def add_circle(self, square, **kwargs):
        name = '{}-circle'.format(chess.SQUARE_NAMES[square])
        xc, yc = self._square_offset(square)
        circle = self.dwg.circle(id=name, center=(xc+4, yc+4), r=3.5, **kwargs)
        self._circles.add(circle)

    def add_arrow(self, source, dest, **kwargs):

        x1, y1 = self._square_offset(source)
        x2, y2 = self._square_offset(dest)
        name = '{}{}-arrow'.format(chess.SQUARE_NAMES[source], chess.SQUARE_NAMES[dest])

        line = self.dwg.line(start=(x1+4, y1+4), end=(x2+4, y2+8), id=name, **kwargs)
        line.set_markers((None, None, self.marker))
        self._arrows.add(line)

    def set_square_color(self, square, color):
        found = False
        for s in (self._squares.elements):
            if s['id'] == chess.SQUARE_NAMES[square]:
                found = True
                break
        if not found:
            raise ValueError(square)
        s['style'] = 'fill:{};'.format(color)

def basic_shapes():
    svg = SvgBoard(size=800, labels=True)
    board = chess.Board()
    for square, piece in board.piece_map().items():
        svg.add_piece(square, piece)
        #svg.add_circle(square, stroke='orange')
    svg.add_legend()
    svg.add_arrow(0, 16)
    #svg.set_square_color(32, 'red')
    #svg.set_square_color(63, 'yellow')
    svg.add_title("HELLO", 'http://example.com')
    svg.add_caption("bye")

    return svg

basic_shapes()
