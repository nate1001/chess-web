
#package
import psycopg2
import psycopg2.extras
import psycopg2.extensions

import chess

#local

import sys
sys.path.append('../pgchess')
from db import Connection
Connection.connect('www-data')

class Query(Connection):

    @classmethod
    def random_search(cls):
        c = Connection.cursor()
        n, rows = cls.execute("select * from random_search()")
        for row in rows:
            yield PositionResult(row)

    @classmethod
    def random_position(cls):
        c = Connection.cursor()
        n, rows = cls.execute("select * from v_position order by random() limit 1")
        if n == 0:
            return None
        for row in rows:
            return Position(row)

    @classmethod
    def select_fen(cls, fen):

        c = Connection.cursor()
        n, rows = cls.execute("select * from v_position where fen=%s limit 1", fen)
        if n == 0:
            return None
        return Position(rows.fetchone())

    @classmethod
    def canonical_pawns(cls):
        n, rows = cls.execute('SELECT n, board FROM kmode ORDER BY pcount(board) DESC, pawn_distance(board)')
        return rows.fetchall()


class Position(Connection):

    #heatmapgen = Heatmap()

    green = ['#f7fcfd', '#e5f5f9', '#ccece6', '#99d8c9', '#66c2a4', '#41ae76', '#238b45', '#006d2c', '#00441b',]
    red = ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026',]
    red.reverse()
    colors = red + ['#ffffff'] + green

    def __init__(self, row):
        self.id = None
        self.site = row['site']
        self.board = row['fen']

        self.score = row['score']
        self.scores = row['scores']
        self.keypieces = row['keypieces']
        self.mobility = row['mobility']
        self.diff = row['diff']
        #self.attacks = row['attacks']

        if self.board.turn:
            self.side = 'w'
        else:
            self.side = 'b'

    def __str__(self):
        return "<Position '{}'>".format(self.board.fen())


    def squareset(self, piecesquares):
        #board = chess.Board(board_fen=None)
        s = chess.SquareSet(0)
        for piece in self._iter_array(piecesquares):
            p = chess.Piece.from_symbol(piece[0])
            sq = chess.SQUARE_NAMES.index(piece[1:])
            #board.set_piece_at(d, p)
            s.add(sq)
        return s

    def to_svg(self, size, query=None, labels=False):
        svg = SvgBoard(size=size, labels=labels)

        for score, (square, piece) in zip(self.scores, self._iter_piecesquares()):
            svg.add_piece(square, piece)
            #if square in [k.square for k in self.keypieces]:
            #    if 0:#piecesquareif hasattr(self, 'querykey') and square in [s.square for s in self.querykey]:
            #        svg.add_circle(square, stroke='green')
            #    else:
            #        svg.add_circle(square)
            if query:
                for square, val in self.occupancy_map(query).items():
                    if val > 0:
                     svg.add_circle(square, stroke='green')
                for square, val in self.mobility_map(query).items():
                    if val > 0:
                         svg.set_square_color(square, self.green[val])
                    if val < 0:
                         svg.set_square_color(square, self.red[val])

            #color = self.heatmapgen.color(score)
            #if color:
            #    svg.set_square_color(square, color)

        svg.add_legend()
        if not hasattr(self, 'distance'):
            self.distance=None
        svg.add_title("{} {} {} {}".format(self.side, self.distance, round(self.score*.01, 2), self.site))
        svg.add_caption("{}".format(self.board.fen()))
        #svg.add_arrow(0, 16)
        #svg.add_title("HELLO", 'http://example.com')
        #svg.add_caption("bye")
        return svg.tostring()

    def occupancy_map(self, query):
        d = {}
        for i in range(64):
            d[i] = 0
            p  = self.board.piece_at(i)
            q  = query.board.piece_at(i)
            if q:
                if q == p:
                    d[i] += 1
                else:
                    d[i] -= 1
            elif p:
                d[i] -= 1
        return d

    def mobility_map(self, query):
        d = {}
        for i in range(64):
            d[i] = 0
    
        for ps in query.mobility:
            if ps in self.mobility:
                d[ps.square] += 1
            else:
                d[ps.square] -= 1
        for ps in self.mobility:
            if ps not in query.mobility:
                d[ps.square] -= 1

        return d
    

class PositionResult(Position):
    def __init__(self, row):
        super().__init__(row)
        self.distance = round(row['distance'], 3)
        self.querykey = row['querykey']
        self.queryboard = row['queryboard'] 

    def __str__(self):
        return "<PositionResult '{}'>".format(self.board.fen())

l = []
for row in Query.canonical_pawns():
    l.append(row)
print(l)




