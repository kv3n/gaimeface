from datetime import timedelta
from gameenums import *
from behavior import *


class PlayData:
    def __init__(self):
        self.quarter = 1
        self.offense_team = Team.NONE
        self.defense_team = Team.NONE
        self.time_left = timedelta(minutes=0, seconds=0)
        self.play_type = PlayType.NONE
        self.play_description = ''
        self.statistical_behavior = None
        self.actual_behavior = 0

    def is_active_play(self):
        return (self.play_type != PlayType.TIMEOUT and
                self.play_type != PlayType.QUARTER and
                self.play_type != PlayType.TWOMINUTE)

    def calculate_statistical_behavior(self):
        self.statistical_behavior = Behavior()
        
        self.statistical_behavior.expected_outcome = random.randint(0,1) # to test basic emotion model
        self.statistical_behavior.utility = random.uniform(0,1) # to test basic emotion model
        self.statistical_behavior.probability = random.uniform(0,1) # to test basic emotion model

    def __str__(self):
        return (str(self.quarter) + ' ' + str(self.time_left) + ' ' + str(self.play_type) + ' ' +
                str(self.offense_team) + ' ' + str(self.defense_team) + '\t' +
                self.play_description)
