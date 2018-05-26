import psycopg2
import psycopg2.extras

import chess
import chess.svg

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
        n, rows = cls.execute(c, "select * from v_position where fen=%s", fen)
        if n == 0:
            return None
        for row in rows:
            return Position(row)


class Position(Connection):
    '''
    DROP VIEW IF EXISTS v_position;
    CREATE VIEW v_position AS
        SELECT 
             site
            ,fen
            ,side(fen)
            ,score
            ,scores
            ,pieces(fen)::square[] AS squares
            ,pieces(fen)::cpiece[]
            ,keypieces::square[] AS keysquares
            ,keypieces::cpiece[]
        FROM POSITION p
    ;
    '''
    heatgen = Heatmap()

    def _iter_array(self, array):

        for piece in array[1:-1].split(','):
            yield piece

    def _parse_pieces(self, pieces):
        l = []
        for p in self._iter_array(pieces):
            l.append(chess.Piece.from_symbol(p))
        return l

    def _parse_squares(self, squares):
        l = []
        for s in self._iter_array(squares):
            l.append(chess.SQUARE_NAMES.index(s))
        return l


    def __init__(self, row):
        self.id = None
        self.site = row['site']
        self.board = chess.Board(row['fen'] + ' 1 1')
        self.side = row['side']
        self.score = row['score']
        self.scores = row['scores']

        self.squares = self._parse_squares(row['squares'])
        self.pieces = self._parse_pieces(row['pieces'])
        self.keysquares = self._parse_squares(row['keysquares'])
        self.keypieces = self._parse_pieces(row['keypieces'])

        self.heatmap = {}
        for square, color in zip(self.keysquares, self.heatgen.gen(self)):
            name = chess.SQUARE_NAMES[square]
            self.heatmap[name] = color

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
    
    def svg(self, id=None, **kwargs):
        sl = '<rect class="square light {}" fill="#ffce9e"'
        sd = '<rect class="square dark {}" fill="#d18b47"'

        rl = '<rect class="square light {}" fill="{}"'
        rd = '<rect class="square dark {}" fill="{}"'

        style = ''

        circles = []
        for square in self.keysquares:
            circles.append((square, square))

        txt = chess.svg.board(self.board, arrows=circles, style=style, coordinates=False, **kwargs)

        for key, val in self.heatmap.items():
            txt = txt.replace(sl.format(key), rl.format(key, val))
            txt = txt.replace(sd.format(key), rd.format(key, val))

        if id:
            txt = txt.replace("<svg ", '<svg id="{}"'.format(id))
        return txt

class PositionResult(Position):
    '''
    DROP TYPE t_search_result cascade;
    CREATE TYPE t_search_result AS
    (
         queryboard board
        ,querykey   piecesquare[]
        ,distance   double precision
        ,site       text
        ,fen        board
        ,side       side
        ,score      real
        ,scores     real[]
        ,squares    square[]
        ,pieces     cpiece[]
        ,keysquares square[]
        ,keypieces  cpiece[]
    );
    '''
    def __init__(self, row):
        super().__init__(row)
        self.distance = round(row['distance'], 3)
        self.querykey = row['querykey']
        self.queryboard = chess.Board(row['queryboard'] + ' 1 1')

    def __str__(self):
        return "<PositionResult '{}'>".format(self.board.fen())



Connection.connect()
#p = Query.select_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
#for row in (Query.random_search())[1]:
#    print(PositionResult(row))

pos = Query.random_position()
print(pos.scores)
print(pos.squares)
print(pos.pieces)
#print(pos.svg())
#print(heat.gen(pos))
#


