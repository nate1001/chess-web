import time

#package
import chess

#local
import reflection

import sys
sys.path.append('../db')
from db import Connection

reflection.database.connect('www-data')
Connection.register_orm(reflection.database.connection())

EcoName = reflection.VEcoName
GameState = reflection.VGamestate
OpeningVar3Agg = reflection.VOpeningVar3Agg

KModePawn = reflection.VKmodePawn
KModeAggPawn = reflection.VKmodeAggPawn
KclassEcoNamePawn = reflection.VKclassEcoNamePawn
KclassEcoVar1Pawn = reflection.VKclassEcoVar1Pawn

KModeWmg = reflection.VKmodeWmg
KModeAggWmg = reflection.VKmodeAggWmg
KclassEcoNameWmg = reflection.VKclassEcoNameWmg
KclassEcoVar1Wmg = reflection.VKclassEcoVar1Wmg

KModeBmg = reflection.VKmodeBmg
KModeAggBmg = reflection.VKmodeAggBmg
KclassEcoNameBmg = reflection.VKclassEcoNameBmg
KclassEcoVar1Bmg = reflection.VKclassEcoVar1Bmg

Position = reflection.VPosition

Game = reflection.VGame
@property
def _(self):
    return '{} ({}) {}'.format(self.wplayer, self.wrating, self.wdiff)
Game.white_name = _

@property
def _(self):
    return '{} ({}) {}'.format(self.bplayer, self.brating, self.bdiff)
Game.black_name = _

@property
def _(self):
    return '{} {}'.format(self.time_control, self.termination)
Game.result_name = _

@property
def _(self):
    return '{} ({}) vs {} ({})'.format(
            self.wplayer, self.wrating,
            self.bplayer, self.brating)
Game.title = _


def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        sys.stderr.write('func:%r args:[%r, %r] took: %2.4f sec\n' % \
          (f.__name__, args, kw, te-ts))
        return result
    return timed

#green = ['#f7fcfd', '#e5f5f9', '#ccece6', '#99d8c9', '#66c2a4', '#41ae76', '#238b45', '#006d2c', '#00441b',]
#red = ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026',]
#red.reverse()
#colors = red + ['#ffffff'] + green
