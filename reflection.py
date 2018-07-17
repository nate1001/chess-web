from peewee import *
from playhouse.postgres_ext import *

database = PostgresqlDatabase('chess', **{})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class VEcoName(BaseModel):
    eco = CharField(null=True)
    eco_name = TextField(null=True)
    fen = Field(null=True)
    halfmoves = IntegerField(null=True)
    moves = TextField(null=True)
    name = TextField(null=True)
    openingid = IntegerField(null=True)
    var1 = TextField(null=True)
    var2 = TextField(null=True)
    var3 = TextField(null=True)

    class Meta:
        table_name = 'v_eco_name'
        primary_key = False

class VEcoVar1(BaseModel):
    eco = CharField(null=True)
    eco_name = TextField(null=True)
    fen = Field(null=True)
    halfmoves = IntegerField(null=True)
    moves = TextField(null=True)
    name = TextField(null=True)
    var1 = TextField(null=True)
    var2 = TextField(null=True)
    var3 = TextField(null=True)

    class Meta:
        table_name = 'v_eco_var1'
        primary_key = False

class VEcoVar2(BaseModel):
    eco = CharField(null=True)
    eco_name = TextField(null=True)
    fen = Field(null=True)
    halfmoves = IntegerField(null=True)
    moves = TextField(null=True)
    name = TextField(null=True)
    var1 = TextField(null=True)
    var2 = TextField(null=True)
    var3 = TextField(null=True)

    class Meta:
        table_name = 'v_eco_var2'
        primary_key = False

class VEcoVar3(BaseModel):
    eco = CharField(null=True)
    fen = Field(null=True)
    halfmoves = IntegerField(null=True)
    meta = TextField(null=True)
    moves = TextField(null=True)
    name = TextField(null=True)
    openingid = IntegerField(null=True)
    var1 = TextField(null=True)
    var2 = TextField(null=True)
    var3 = TextField(null=True)

    class Meta:
        table_name = 'v_eco_var3'
        primary_key = False

class VGame(BaseModel):
    bdiff = IntegerField(null=True)
    bmg_class = IntegerField(null=True)
    bplayer = TextField(null=True)
    brating = IntegerField(null=True)
    date_ = DateField(null=True)
    event = TextField(null=True)
    gameid = TextField(null=True)
    moves = ArrayField(field_class=TextField, null=True)
    openingid = IntegerField(null=True)
    pawn_class = IntegerField(null=True)
    pclass = IntegerField(null=True)
    result = Field(null=True)
    round = IntegerField(null=True)
    termination = TextField(null=True)
    time_control = TextField(null=True)
    wdiff = IntegerField(null=True)
    wmg_class = IntegerField(null=True)
    wplayer = TextField(null=True)
    wrating = IntegerField(null=True)

    class Meta:
        table_name = 'v_game'
        primary_key = False

class VGameOpening(BaseModel):
    fen = Field(null=True)
    gameid = TextField(null=True)
    name = TextField(null=True)
    openingid = IntegerField(null=True)
    var1 = TextField(null=True)
    var2 = TextField(null=True)
    var3 = TextField(null=True)

    class Meta:
        table_name = 'v_game_opening'
        primary_key = False

class VGamestate(BaseModel):
    eg = Field(null=True)
    gameid = TextField(null=True)
    last = Field(null=True)
    mg = Field(null=True)
    openingid = IntegerField(null=True)
    pawn_class = IntegerField(null=True)
    wmg_class = IntegerField(null=True)

    class Meta:
        table_name = 'v_gamestate'
        primary_key = False

class VKmode(BaseModel):
    avg = DecimalField(null=True)
    count = BigIntegerField(null=True)
    gameid = TextField(null=True)
    hamming = BigIntegerField(null=True)
    jaccard = FloatField(null=True)
    pawn_centroid = Field(null=True)
    pawn_class = IntegerField(null=True)
    pawns = Field(null=True)
    stddev = DecimalField(null=True)

    class Meta:
        table_name = 'v_kmode'
        primary_key = False

class VKmodeAgg(BaseModel):
    avg = DecimalField(null=True)
    count = BigIntegerField(null=True)
    draw = DecimalField(null=True)
    eco_name = ArrayField(field_class=TextField, null=True)
    eco_var1 = ArrayField(field_class=TextField, null=True)
    jaccard = DecimalField(null=True)
    lose = DecimalField(null=True)
    pawn_centroid = Field(null=True)
    pawn_class = IntegerField(null=True)
    rating = FloatField(null=True)
    stddev = DecimalField(null=True)
    win = DecimalField(null=True)

    class Meta:
        table_name = 'v_kmode_agg'
        primary_key = False

class VOpeningNameAgg(BaseModel):
    count = BigIntegerField(null=True)
    eco_name = TextField(null=True)
    fen = Field(null=True)
    name = TextField(null=True)
    openingid = IntegerField(null=True)
    rating_mu = IntegerField(null=True)
    win_pct = DecimalField(null=True)

    class Meta:
        table_name = 'v_opening_name_agg'
        primary_key = False

class VOpeningTop(BaseModel):
    count = BigIntegerField(null=True)
    eco_name = TextField(null=True)
    fen = Field(null=True)
    halfmoves = IntegerField(null=True)
    moves = TextField(null=True)
    name = TextField(null=True)
    var1 = TextField(null=True)
    var2 = TextField(null=True)
    var3 = TextField(null=True)

    class Meta:
        table_name = 'v_opening_top'
        primary_key = False

class VOpeningVar1Agg(BaseModel):
    count = BigIntegerField(null=True)
    eco_name = TextField(null=True)
    fen = Field(null=True)
    name = TextField(null=True)
    openingid = IntegerField(null=True)
    rating_mu = IntegerField(null=True)
    var1 = TextField(null=True)
    win_pct = DecimalField(null=True)

    class Meta:
        table_name = 'v_opening_var1_agg'
        primary_key = False

class VOpeningVar1Top(BaseModel):
    count = BigIntegerField(null=True)
    eco_name = TextField(null=True)
    name = TextField(null=True)
    var1 = TextField(null=True)
    var2 = TextField(null=True)
    var3 = TextField(null=True)

    class Meta:
        table_name = 'v_opening_var1_top'
        primary_key = False

class VOpeningVar2Agg(BaseModel):
    count = BigIntegerField(null=True)
    eco_name = TextField(null=True)
    fen = Field(null=True)
    name = TextField(null=True)
    openingid = IntegerField(null=True)
    rating_mu = IntegerField(null=True)
    var1 = TextField(null=True)
    var2 = TextField(null=True)
    win_pct = DecimalField(null=True)

    class Meta:
        table_name = 'v_opening_var2_agg'
        primary_key = False

class VOpeningVar3Agg(BaseModel):
    count = BigIntegerField(null=True)
    eco = CharField(null=True)
    eco_name = TextField(null=True)
    fen = Field(null=True)
    halfmoves = IntegerField(null=True)
    moves = TextField(null=True)
    name = TextField(null=True)
    openingid = IntegerField(null=True)
    rating_mu = IntegerField(null=True)
    system_cnt = DecimalField(null=True)
    var1 = TextField(null=True)
    var2 = TextField(null=True)
    var3 = TextField(null=True)
    win_pct = DecimalField(null=True)

    class Meta:
        table_name = 'v_opening_var3_agg'
        primary_key = False

class VOpeningVar3Top(BaseModel):
    count = BigIntegerField(null=True)
    eco = CharField(null=True)
    fen = Field(null=True)
    halfmoves = IntegerField(null=True)
    meta = TextField(null=True)
    moves = TextField(null=True)
    name = TextField(null=True)
    openingid = IntegerField(null=True)
    var1 = TextField(null=True)
    var2 = TextField(null=True)
    var3 = TextField(null=True)

    class Meta:
        table_name = 'v_opening_var3_top'
        primary_key = False

class VPawnBoard(BaseModel):
    fen = Field(null=True)
    gameid = TextField(null=True)
    pawn_class = IntegerField(null=True)
    pawns = Field(null=True)

    class Meta:
        table_name = 'v_pawn_board'
        primary_key = False

class VPclassEcoName(BaseModel):
    count = BigIntegerField(null=True)
    eco = CharField(null=True)
    eco_name = TextField(null=True)
    fen = Field(null=True)
    group = DecimalField(null=True)
    moves = TextField(null=True)
    openingid = IntegerField(null=True)
    pawn_class = IntegerField(null=True)
    system = TextField(null=True)

    class Meta:
        table_name = 'v_pclass_eco_name'
        primary_key = False

class VPclassEcoVar1(BaseModel):
    count = BigIntegerField(null=True)
    eco = CharField(null=True)
    eco_name = TextField(null=True)
    fen = Field(null=True)
    group = DecimalField(null=True)
    moves = TextField(null=True)
    openingid = IntegerField(null=True)
    pawn_class = IntegerField(null=True)
    system = TextField(null=True)

    class Meta:
        table_name = 'v_pclass_eco_var1'
        primary_key = False

class VPosition(BaseModel):
    fen = Field(null=True)
    gameid = TextField(null=True)

    class Meta:
        table_name = 'v_position'
        primary_key = False

