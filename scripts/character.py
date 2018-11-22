from behavior import *
from playchart import *
from gamedatadump import *
import json


class Character:
    def __init__(self, sketch_file, emotion_model):
        self.emotion_model = emotion_model

        self.sketch = {}
        with open(sketch_file + '.json') as sketch_data:
            self.sketch = json.load(sketch_data)

        self.alpha = 0
        self.beta = 0
        if self.sketch['football'] > 0:
            game_fair = self.sketch['game_fair']
            if game_fair < 0.25:
                self.alpha = game_fair
                self.beta = game_fair
            elif self.sketch['game_fair'] > 0.75:
                self.alpha = game_fair
                self.beta = 1.0 - game_fair
            else:
                self.alpha = 0.5
                self.beta = 0.5

    def __get_utility_for(self, play: PlayData):
        team_score = play.offense_team_score  # This only works because we are considering only offense
        opponent_score = play.defense_team_score  # This only works because we are considering only offense

        if team_score == 0 and opponent_score == 0:
            utility = 1.0
        else:
            utility = (team_score -
                       self.alpha * (max(opponent_score - team_score, 0)) -
                       self.beta * (max(team_score - opponent_score, 0))
                       ) / max(team_score, opponent_score)

        print(str(team_score) + ' - ' + str(opponent_score) + ' -> ' + str(utility))

        return utility

    def determine_utilities_for(self, play: PlayData):
        predicted_behavior = Behavior()

        predicted_behavior.expected_outcome = random.randint(0, 1)  # if our team we want this to be one

        predicted_behavior.utility = self.__get_utility_for(play)  # based on fair-scmidt we have utilities

        # eo = (((1 - present_or_past) * probability of winning) + (present_or_past * probability of winning at beginning of game)) 
        # + positive_development - (negative_development-coping_for_team)

        # For example:
        # eo = ((((1 - 0.5) * 0) + (0.5 * 0.7)) + 0.0 - (0 - 0)) # for my own team
        # if (eo > 1):
        #     eo = 1
        # elif (eo < 0):
        #     eo = 0

        # Need eo for the play of the other team if we have time
        predicted_behavior.probability = random.uniform(0,1) # will be equal to the eo

        return predicted_behavior

    def set_emotion_mode(self, new_emotion_model):
        self.emotion_model = new_emotion_model

    def get_emotion_for(self, play):
        predicted_behavior = self.determine_utilities_for(play)

        # Compare here with statistical behavior
        return self.emotion_model.process(predicted_behavior=predicted_behavior,
                                          statistical_behavior=play.statistical_behavior,
                                          actual_behavior=play.actual_behavior)


