import time

#package
import chess

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Text
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.ext.declarative import declarative_base

#local
import sys
sys.path.append('../db')
from db import Connection

db_uri = 'postgres:///chess'
engine = create_engine(db_uri)
metadata = MetaData()
metadata.reflect(bind=engine)
Connection.register_alchemy(engine)
Base = declarative_base(metadata=metadata)

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)


def timeit(f):

    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        sys.stderr.write('func:%r args:[%r, %r] took: %2.4f sec\n' % \
          (f.__name__, args, kw, te-ts))
        return result
    return timed


KmodeAgg = Table('m_kmode_agg', metadata, autoload_with=engine)
Kmode = Table('m_kmode', metadata, autoload_with=engine)
OpeningVar3Agg = Table('v_opening_var3_agg', metadata, autoload_with=engine)
PclassEcoName = Table('v_pclass_eco_name', metadata, autoload_with=engine)
PclassEcoVar1 = Table('v_pclass_eco_var1', metadata, autoload_with=engine)
PawnBoard = Table('v_pawn_board', metadata, autoload_with=engine)
GameState = Table('v_gamestate', metadata, autoload_with=engine)

class EcoName(Base):
    __table__ = Table('v_eco_name', 
            metadata,
            Column('name', Text, primary_key=True),
            autoload=True,
            autoload_with=engine,
            )
    
    @property
    def board(self):
        return self.fen
    

class Query(Connection):


    @classmethod
    def eco_agg(self, pclass, opening=False, var=False):

        if var:
            table = 'v_eco_var'
        elif opening:
            table = 'v_eco_opening'
        else:
            table = 'v_pclass_eco_name'

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


class Position(Connection):

    #heatmapgen = Heatmap()

    green = ['#f7fcfd', '#e5f5f9', '#ccece6', '#99d8c9', '#66c2a4', '#41ae76', '#238b45', '#006d2c', '#00441b',]
    red = ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026',]
    red.reverse()
    colors = red + ['#ffffff'] + green

    def __init__(self, row):
        self.id = None
        self.site = row['gameid']
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
    

class Game:

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

#game = Query.random_game()
#print(game)




