import psycopg2
import psycopg2.extras
import psycopg2.extensions

import chess
import chess.svg

#local
from svgboard import SvgBoard
from heatmap import Heatmap

class Connection:
    conn_string = "host='localhost' dbname='chess' user='www-data' password='NULL'"
    conn = None

    @classmethod
    def connect(cls):
        cls.conn = psycopg2.connect(cls.conn_string)

    @classmethod
    def cursor(cls):
        return cls.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    @classmethod
    def execute(cls, cursor, query, *params):
        cursor.execute(query, params)
        return cursor.rowcount, cursor

    @classmethod
    def get_type_oid(cls, name):
        curs = cls.cursor()
        n, curs = cls.execute(curs, 'select oid from pg_type where typname = %s', name)
        if n==0:
            raise ValueError("could not find type {}".format(name))
        return curs.fetchone()['oid']

    @classmethod
    def register_type(cls, name, func):
        oids = (Connection.get_type_oid(name),) 
        f = psycopg2.extensions.new_type(oids, name, func)
        psycopg2.extensions.register_type(f)
        oids = (Connection.get_type_oid("_"+name),) 
        f = psycopg2.extensions.new_array_type(oids, "_"+name, f)
        psycopg2.extensions.register_type(f)


Connection.connect()

class PieceSquare:
    def __init__(self, val):

        self.piece = chess.Piece.from_symbol(val[0])
        self.square = chess.SQUARE_NAMES.index(val[1:])

    def __str__(self):
        return '{}{}'.format(self.piece, chess.SQUARE_NAMES[self.square])

    def __repr__(self):
        return self.__str__()

class PieceSquareSubject:

    def __init__(self, val):
        val = list(val)
        self.subject = chess.Piece.from_symbol(val.pop(0))
        self.kind = val.pop(0)
        self.piece = chess.Piece.from_symbol(val.pop(0))
        self.square = chess.SQUARE_NAMES.index(''.join(val))

    def __str__(self):
        return '{}{}{}{}'.format(
                self.subject, self.kind, self.piece, chess.SQUARE_NAMES[self.square])

    def __repr__(self):
        return self.__str__()


def db_to_square(val, curs):
    return chess.SQUARE_NAMES.index(val)
Connection.register_type("square", db_to_square)

def db_to_cpiece(val, curs):
    return chess.Piece.from_symbol(val)
Connection.register_type("cpiece", db_to_cpiece)

def db_to_board(val, curs):
    return chess.Board(val + ' 1 1')
Connection.register_type("board", db_to_board)

def db_to_piecesquare(val, curs):
    for v in '>/-':
        if v in val:
            return PieceSquareSubject(val)
    return PieceSquare(val)

Connection.register_type("piecesquare", db_to_piecesquare)


class Query(Connection):

    @classmethod
    def random_search(cls):
        c = Connection.cursor()
        n, rows = cls.execute(c, "select * from random_search()")
        for row in rows:
            yield PositionResult(row)

    @classmethod
    def random_position(cls):
        c = Connection.cursor()
        n, rows = cls.execute(c, "select * from v_position order by random() limit 1")
        if n == 0:
            return None
        for row in rows:
            return Position(row)

    @classmethod
    def select_fen(cls, fen):

        c = Connection.cursor()
        n, rows = cls.execute(c, "select * from v_position where fen=%s limit 1", fen)
        if n == 0:
            return None
        return Position(rows.fetchone())


class Position(Connection):

    heatmapgen = Heatmap()

    def __init__(self, row):
        self.id = None
        self.site = row['site']
        self.board = row['fen']
        self.score = row['score']
        self.scores = row['scores']
        self.keypieces = row['keypieces']
        self.attacks = row['attacks']

        if self.board.turn:
            self.side = 'w'
        else:
            self.side = 'b'


    def __str__(self):
        return "<Position '{}'>".format(self.board.fen())

    def _iter_piecesquares(self):
        for i in range(64):
            bb = (56 - (i//8)*8 + (i%8))
            p = self.board.piece_at(bb)
            if p:
                yield bb, p


    def squareset(self, piecesquares):
        #board = chess.Board(board_fen=None)
        s = chess.SquareSet(0)
        for piece in self._iter_array(piecesquares):
            p = chess.Piece.from_symbol(piece[0])
            sq = chess.SQUARE_NAMES.index(piece[1:])
            #board.set_piece_at(d, p)
            s.add(sq)
        return s

    def to_svg(self, size, labels=False):
        svg = SvgBoard(size=size, labels=labels)

        for score, (square, piece) in zip(self.scores, self._iter_piecesquares()):
            svg.add_piece(square, piece)
            if square in [k.square for k in self.keypieces]:
                if hasattr(self, 'querykey') and square in [s.square for s in self.querykey]:
                    svg.add_circle(square, stroke='green')
                else:
                    svg.add_circle(square)

            color = self.heatmapgen.color(score)
            if color:
                svg.set_square_color(square, color)
        svg.add_legend()
        if not hasattr(self, 'distance'):
            self.distance=None
        svg.add_title("{} {} {} {}".format(self.side, self.distance, round(self.score*.01, 2), self.site))
        svg.add_caption("{}".format(self.board.fen()))
        #svg.add_arrow(0, 16)
        #svg.add_title("HELLO", 'http://example.com')
        #svg.add_caption("bye")
        return svg.tostring()
    

class PositionResult(Position):
    def __init__(self, row):
        super().__init__(row)
        self.distance = round(row['distance'], 3)
        self.querykey = row['querykey']
        self.queryboard = row['queryboard'] 

    def __str__(self):
        return "<PositionResult '{}'>".format(self.board.fen())




