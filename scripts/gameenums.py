from enum import Enum


class Team(Enum):
    SF = 'SF'
    CHI = 'CHI'
    CIN = 'CIN'
    BUF = 'BUF'
    DEN = 'DEN'
    CLE = 'CLE'
    ARI = 'ARI'
    LAC = 'LAC'
    KC = 'KC'
    IND = 'IND'
    DAL = 'DAL'
    MIA = 'MIA'
    PHI = 'PHI'
    ATL = 'ATL'
    NYG = 'NYG'
    JAX = 'JAX'
    NYJ = 'NYJ'
    DET = 'DET'
    GB = 'GB'
    CAR = 'CAR'
    NE = 'NE'
    OAK = 'OAK'
    LAR = 'LAR'
    BAL = 'BAL'
    WAS = 'WAS'
    NO = 'NO'
    SEA = 'SEA'
    PIT = 'PIT'
    TB = 'TB'
    HOU = 'HOU'
    TEN = 'TEN'
    MIN = 'MIN'
    NONE = 'NONE'

class Emotions(Enum):
    NEUTRAL = 0
    HAPPY = 1
    SAD = 2
    FEAR = 3
    ANGER = 4

class PlayType(Enum):
    RUSH = 'RUSH'
    PUNT = 'PUNT'
    PASS = 'PASS'
    FIELDGOAL = 'FIELD GOAL'
    EXTRAPOINT = 'EXTRA POINT'
    SACK = 'SACK'
    SCRAMBLE = 'SCRAMBLE'
    NOPLAY = 'NO PLAY'
    FUMBLE = 'FUMBLES'
    QBKNEEL = 'QB KNEEL'
    TWOPOINT = 'TWO-POINT CONVERSION'
    KICKOFF = 'KICK OFF'
    CLOCKSTOP = 'CLOCK STOP'
    QUARTER = 'QUARTER'
    PENALTY ='PENALTY'
    EXCEPTION = 'EXCEPTION'
    TWOMINUTE = 'TWOMINUTE'
    TIMEOUT = 'TIMEOUT'
    NONE = 'NONE'
