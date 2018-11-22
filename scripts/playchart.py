from datetime import timedelta
from gameenums import *
from behavior import *

class PlayData:
    def __init__(self, csv_row):
        self.quarter = csv_row['Quarter']

        self.time_left = timedelta(minutes=csv_row['Minute'], seconds=csv_row['Second'])
        self.play_type = PlayType(csv_row['PlayType'])
        self.play_description = csv_row['Description']
        self.statistical_behavior = None
        self.actual_behavior = 0
        self.down = csv_row['Down']
        self.to_go = csv_row['ToGo']
        self.yards = csv_row['Yards']
        self.is_incomplete = csv_row['IsIncomplete']
        self.play_key = str(self.down) + '_'
        to_go_key = self.to_go
        if to_go_key >= 10:
            to_go_key = 10
        self.play_key += str(to_go_key)

        if self.is_active_play():
            self.offense_team = Team(csv_row['OffenseTeam'])
            self.defense_team = Team(csv_row['DefenseTeam'])
        else:
            self.offense_team = Team.NONE
            self.defense_team = Team.NONE

    def is_active_play(self):
        return (self.play_type != PlayType.TIMEOUT and
                self.play_type != PlayType.QUARTER and
                self.play_type != PlayType.TWOMINUTE)

    def calculate_statistical_behavior(self, successful_play_prob, total_plays):
        self.statistical_behavior = Behavior()

        successes = 0
        plays = 0
        for key, value in successful_play_prob.items():
            key_down = int(key.split('_')[0])
            key_togo = int(key.split('_')[1])
            if (key_down >= self.down and key_togo > self.to_go) or (key_togo == 10 and key_down >= self.down):
                successes += value
        for key, value in total_plays.items():
            key_down = int(key.split('_')[0])
            key_togo = int(key.split('_')[1])
            if (key_down >= self.down and key_togo > self.to_go) or (key_togo == 10 and key_down >= self.down):
                plays += value

        self.statistical_behavior.expected_outcome = random.randint(0,1) # to test basic emotion model
        self.statistical_behavior.utility = random.uniform(0,1) # to test basic emotion model

        if plays > 0:
            self.statistical_behavior.probability = successes / plays

    def __str__(self):
        return (str(self.quarter) + ' ' + str(self.time_left) + ' ' + str(self.play_type) + ' ' +
                str(self.offense_team) + ' ' + str(self.defense_team) + '\t' + self.play_description + ' -> Chance: ' +
                str(self.statistical_behavior.probability))
