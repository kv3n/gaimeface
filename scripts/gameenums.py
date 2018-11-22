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
    SD = 'SD'   # This is because LAC was called SD before
    KC = 'KC'
    IND = 'IND'
    DAL = 'DAL'
    MIA = 'MIA'
    PHI = 'PHI'
    ATL = 'ATL'
    NYG = 'NYG'
    JAC = 'JAC'  # Alternate JAC team
    JAX = 'JAX'
    NYJ = 'NYJ'
    DET = 'DET'
    GB = 'GB'
    CAR = 'CAR'
    NE = 'NE'
    OAK = 'OAK'
    LA = 'LA'
    STL = 'STL'  # Diff rams names
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
    NONE = 'NA'

class Emotions(Enum):
    NEUTRAL = 0
    HAPPY = 1
    SAD = 2
    FEAR = 3
    ANGER = 4

class PlayType(Enum):
    RUSH = 'Run'
    PUNT = 'Punt'
    PASS = 'Pass'
    FIELDGOAL = 'Field Goal'
    EXTRAPOINT = 'Extra Point'
    SACK = 'Sack'
    NOPLAY = 'No Play'
    QBKNEEL = 'QB Kneel'
    TWOMINUTE = 'Two Minute Warning'
    KICKOFF = 'Kickoff'
    SPIKE = 'Spike'
    QUARTER = 'Quarter End'
    HALF = 'Half End'
    END = 'End of Game'
    TIMEOUT = 'Timeout'
    NONE = 'NONE'
