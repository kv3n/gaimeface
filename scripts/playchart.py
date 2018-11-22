from datetime import timedelta
from gameenums import *
from behavior import *

class PlayData:
    def __init__(self, csv_row):
        self.quarter = csv_row['qtr']

        self.time_left = timedelta(minutes=int(csv_row['time'].split(':')[0]), seconds=int(csv_row['time'].split(':')[1]))
        self.play_type = PlayType(csv_row['PlayType'])
        self.play_description = csv_row['desc']
        self.statistical_behavior = None
        self.down = int(csv_row['down'])
        self.to_go = int(csv_row['ydstogo'])
        self.yards = int(csv_row['Yards.Gained'])
        self.is_complete = (csv_row['PassOutcome'] == 'Complete') or (csv_row['PuntResult'] == 'Clean') or (csv_row['ExPointResult'] == 'Made') or (csv_row['FieldGoalResult'] == 'Good') or (self.yards > 0)
        self.play_key = str(self.down) + '_'
        to_go_key = self.to_go
        if to_go_key >= 10:
            to_go_key = 10
        self.play_key += str(to_go_key)
        self.offense_team_score = int(csv_row['PosTeamScore'])
        self.defense_team_score = int(csv_row['DefTeamScore'])

        self.win_probability = csv_row['Win_Prob']  # This only works because we consider offense

        # Extra Emotion Variables
        self.is_touchdown = int(csv_row['Touchdown'])
        self.is_intercepted = int(csv_row['InterceptionThrown'])
        self.is_exciting_fieldgoal = (self.play_type == PlayType.FIELDGOAL) and (self.is_complete) and (csv_row['FieldGoalDistance'] > 40)

        if self.is_active_play():
            self.offense_team = Team(csv_row['posteam'])
            self.defense_team = Team(csv_row['DefensiveTeam'])

        else:
            self.offense_team = Team.NONE
            self.defense_team = Team.NONE

    def is_active_play(self):
        return (self.play_type != PlayType.TIMEOUT and
                self.play_type != PlayType.QUARTER and
                self.play_type != PlayType.TWOMINUTE and
                self.play_type != PlayType.HALF and
                self.play_type != PlayType.END)

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

        self.statistical_behavior.utility = random.uniform(0, 1)  # to test basic emotion model

        if plays > 0:
            self.statistical_behavior.probability = successes / plays
        else:
            self.statistical_behavior.probability = random.uniform(0, 1)

        self.statistical_behavior.compute_expected_outcome()

    def __str__(self):
        return (str(self.quarter) + ' ' + str(self.time_left) + ' ' + str(self.play_type) + ' ' +
                str(self.offense_team) + ' ' + str(self.defense_team) + '\t' + self.play_description + ' -> Chance: ' +
                str(self.statistical_behavior.probability))
