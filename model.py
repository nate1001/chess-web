import time

#package
import psycopg2
import psycopg2.extras
import psycopg2.extensions

import chess

#local

import sys
sys.path.append('../db')
from db import Connection
from svgboard import SvgBoard

Connection.connect('www-data')

def timeit(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        sys.stderr.write('func:%r args:[%r, %r] took: %2.4f sec\n' % \
          (f.__name__, args, kw, te-ts))
        return result
    return timed

class Query(Connection):

    @classmethod
    def _execute_all(cls, query, klass, *args):
        n, rows = cls.execute(query, *args)
        l = []
        for row in rows:
            l.append(klass(row))
        return l

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
    def random_game(cls):
        c = Connection.cursor()
        n, rows = cls.execute("select * from v_game order by random() limit 1")
        if n:
            return Game(rows.fetchone())

    @classmethod
    def select_fen(cls, fen):

        c = Connection.cursor()
        n, rows = cls.execute("select * from v_position where fen=%s limit 1", fen)
        if n == 0:
            return None
        return Position(rows.fetchone())

    @classmethod
    def canonical_pawns(cls):
        n, rows = cls.execute('SELECT * from m_kmode_agg order by count desc')
        l = []
        for row in rows:
            l.append(Centroid(row))
        return l

    @classmethod
    @timeit
    def kmode_positions(self, id):
        n, rows = Connection.execute('select * from v_kmode where pclass=%s order by random() limit 20', id)
        l = []
        for row in rows:
            l.append(CentroidPos(row))
        return l

    @classmethod
    def eco_agg(self, pclass, opening=False, var=False):

        if var:
            table = 'v_eco_var'
        elif opening:
            table = 'v_eco_opening'
        else:
            table = 'v_eco_system'

        n, rows = Connection.execute('select * from {} where pclass=%s'.format(table), pclass)
        l = []
        for row in rows:
            l.append(EcoAgg(row))
        return l

    @classmethod
    def openings(cls):
        return cls._execute_all('SELECT * from v_opening_name', Opening)

    @classmethod
    def opening(cls, name):
        q = "SELECT * FROM v_opening_var3_agg WHERE name = %s"
        openings = cls._execute_all(q, Opening, name)
        if not openings:
            return
        return openings

    @classmethod
    def opening_var(cls, number):
        q = "SELECT * FROM v_opening_var3_agg WHERE openingid = %s"
        opening = cls._execute_all(q, Opening, number)
        if not opening:
            return None, None
        q = "SELECT * FROM v_game_lastmove WHERE openingid = %s order by random() limit 50"
        games = cls._execute_all(q, Game, number)
        return opening[0], games

class System:
    def __init__(self, name, openings):
        keys = set()
        self.name = name
        self.openings = {}

        for o in openings:
            keys.add(o.key)

        for k in keys:
            self.openings[k] = []
            last = None
            for o in openings:
                if last and last.key_var:
                    last.same_key_var = last.var == o.var and o.key_var
                if o.key == k:
                    self.openings[k].append(o)
                last = o
        
        self.keys = sorted(self.openings.keys())

class Opening:
    def __init__(self, row):
        #self.ecoid = row['ecoid']
        self.eco = row['eco'][:3]
        self.id = row['openingid']
        self.opening = row['name']
        self.var1 = row['var1'] or ''
        self.var2 = row['var2'] or ''
        self.var3 = row['var3'] or ''
        self.board = row['fen']
        self.moves = row['moves']
        self.halfmoves = row['halfmoves']
        self.system_cnt = row['system_cnt']
        self.rating_mu = row['rating_mu']
        self.win = row['win%']

        self.key = '{}, {}'.format(self.opening, self.var1)
        self.key_opening = not self.var1
        self.key_var = not self.var2
        self.name = ', '.join([n for n in [self.var1, self.var2, self.var3] if n])
        self.subname = ', '.join([n for n in [self.var2, self.var3] if n])
        self.same_key_var = None
        self.same_var = None

    def __str__(self):
        return "<Opening {} {}: {}:{},{},{}>".format(
                self.eco, self.system, self.opening,
                self.var, self.subvar, self.subsubvar)


class EcoAgg:
    def __init__(self, row):
        self.count = row['count']
        self.klass = row['pclass']
        self.system = row['meta']
        if 'opening' in row.keys():
            self.opening = row['opening']
        if 'var' in row.keys():
            self.var = row['var']

class Centroid:

    def __init__(self, row):
        self.count = row['count']
        self.pclass = row['pclass']
        self.avg = round(row['avg'], 1)
        self.stddev = round(row['stddev'], 1)
        self.board = row['pawn_centr']

        if 'win' in row.keys():
            self.eco = row['systems']
            self.win = round(row['win'], 2)
            self.draw = row['draw']
            self.lose = row['lose']
            self.rating = int(row['rating'])

    @timeit
    def to_svg(self, size, href=None):
        return self.board.to_svg(size, href=href).tostring()


class CentroidPos(Centroid):
    def __init__(self, row):
        super().__init__(row)
        self.hamming = row['hamming']
        self.jaccard = round(row['jaccard'], 2)
        self.position = row['pawns']
        self.site = row['site']

    def to_svg(self, size):
        return self.position.to_svg(size, comp=self.board).tostring()


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
        #self.diff = row['diff']
        #self.attacks = row['attacks']

        if self.board.turn:
            self.side = 'w'
        else:
            self.side = 'b'

    def __str__(self):
        return "<Position '{}'>".format(self.board.fen())

    def __iter__(self):
        return self.piecesquares().__iter__()

    @property
    def movenum(self):
        return self.board.fullmove_number

    @property
    def halfmovenum(self):
        o = 1 if self.board.turn == chess.BLACK else 0
        return (self.board.fullmove_number-1) * 2 + o

    @property
    def fen(self):
        return self.board.fen()
    
    def piecesquares(self):
        return [(t[1], t[0]) for t in list(self.board.piece_map().items())]

    def squareset(self, piecesquares):
        #board = chess.Board(board_fen=None)
        s = chess.SquareSet(0)
        for piece in self._iter_array(piecesquares):
            p = chess.Piece.from_symbol(piece[0])
            sq = chess.SQUARE_NAMES.index(piece[1:])
            #board.set_piece_at(d, p)
            s.add(sq)
        return s

    def to_svg(self, size, comp=None, title=None, caption=None, legend=True, fen=True, labels=False):
        return self.board.to_svg(size, comp=comp, title=title, legend=legend, fen=fen, labels=labels).tostring()

        svg = SvgBoard(size=size, labels=labels)
        if title:
            svg.add_title(title)
        if caption:
            svg.add_caption(title)
        else:
            svg.add_caption("{}".format(self.board.fen()))
        for p,s in self.piecesquares():
            svg.add_piece(s, p)

        #for score, (square, piece) in zip(self.scores, self._iter_piecesquares()):
        #    svg.add_piece(square, piece)
        #    #if square in [k.square for k in self.keypieces]:
        #    #    if 0:#piecesquareif hasattr(self, 'querykey') and square in [s.square for s in self.querykey]:
        #    #        svg.add_circle(square, stroke='green')
        #    #    else:
        #    #        svg.add_circle(square)
        #    if query:
        #        for square, val in self.occupancy_map(query).items():
        #            if val > 0:
        #             svg.add_circle(square, stroke='green')
        #        for square, val in self.mobility_map(query).items():
        #            if val > 0:
        #                 svg.set_square_color(square, self.green[val])
        #            if val < 0:
        #                 svg.set_square_color(square, self.red[val])

            #color = self.heatmapgen.color(score)
            #if color:
            #    svg.set_square_color(square, color)

        svg.add_legend()
        if not hasattr(self, 'distance'):
            self.distance=None
        #svg.add_title("{} {} {} {}".format(self.side, self.distance, round(self.score*.01, 2), self.site))
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
    
class PositionMG(Position):
    def __init__(self, row):
        super().__init__(row)
        self.similar = round(row['similar'], 3)

    def __str__(self):
        return "<PositionResult '{}'>".format(self.board.fen())

class PositionResult(Position):
    def __init__(self, row):
        super().__init__(row)
        self.distance = round(row['distance'], 3)
        self.querykey = row['querykey']
        self.queryboard = row['queryboard'] 

    def __str__(self):
        return "<PositionResult '{}'>".format(self.board.fen())

class Game:
    '''
 gameid        | bigint       |           |          | 
 event         | text         |           |          | 
 site          | text         |           |          | 
 date_         | date         |           |          | 
 round         | integer      |           |          | 
 wplayer       | text         |           |          | 
 bplayer       | text         |           |          | 
 result        | gameresult   |           |          | 
 eco           | character(3) |           |          | 
 eco_name      | text         |           |          | 
 variation     | text         |           |          | 
 wdiff         | integer      |           |          | 
 bdiff         | integer      |           |          | 
 wrating       | integer      |           |          | 
 brating       | integer      |           |          | 
 time_control  | text         |           |          | 
 moves         | text         |           |          | 
 #mg_halfmove   | integer      |           |          | 
 eg_halfmove   | integer      |           |          | 
 last_halfmove | integer      |           |          | 
    '''

    def __init__(self, row):
        self.site = row['site']
        self.date = row['date_']
        self.event = row['event']
        self.wplayer = row['wplayer']
        self.bplayer = row['bplayer']
        self.result = row['result']
        self.eco = row['eco']
        self.eco_name = row['eco_name']
        self.variation = row['variation']
        self.wdiff = row['wdiff']
        self.bdiff = row['bdiff']
        self.wrating = row['wrating']
        self.brating = row['brating']
        self.time_control = row['time_control']
        self.moves = row['moves']
        self.board = row['fen']
        #self.mg_halfmove = row['mg_halfmove']
        #self.eg_halfmove = row['eg_halfmove']
        #self.pawn_centr = row['pawn_centr']
        #self.pclass = row['pclass']

        self.h1 = "{} ({})  {} ({})".format(
                self.wplayer, self.wdiff,
                self.bplayer, self.bdiff)

        if len(self.wplayer) > len(self.bplayer):
            self.bplayer += '&nbsp;'*(len(self.wplayer) - len(self.bplayer))
        elif len(self.bplayer) > len(self.wplayer):
            self.wplayer += '&nbsp;'*(len(self.bplayer) - len(self.wplayer))

        self.white = "{} ({}) {}".format(self.wplayer, self.wdiff, self.wrating)
        self.black = "{} ({}) {}".format(self.bplayer, self.bdiff, self.brating)
        self.h2 = "{} {}".format(self.time_control, self.result)



    def __str__(self):
        return "<Game '{}'>".format(self.title())
    
    def __iter__(self):
        for p in self.positions():
            yield p

    @classmethod
    def get(cls, site):
        n, rows = Connection.execute('select * from v_game where site=%s', site)
        if n:
            return cls(rows.fetchone())

    def positions(self):
        n, rows = Connection.execute('select * from v_position_mg where site=%s order by halfmove(fen)', self.site)
        l = []
        for row in rows:
            l.append(PositionMG(row))
        return l

    def title(self):
        return '{} ({}) vs {} ({}) {}'.format(self.wplayer, self.wdiff, self.bplayer, self.bdiff, self.result)

    def subtitle(self):
        return '{} {} - {}: {}'.format(self.event, self.time_control, self.eco, self.eco_name)

#l = []
#for row in Query.canonical_pawns():
#    l.append(row)
#print(l)

#game = Query.random_game()
#print(game)




