from behavior import *
from playchart import *
from gamedatadump import *
import json
import gameviewer


class Character:
    def __init__(self, sketch_file, emotion_model):
        self.emotion_model = emotion_model
        self.debug_info = ''
        self.game = None

        self.sketch = {}
        with open(sketch_file + '.json') as sketch_data:
            self.sketch = json.load(sketch_data)

        self.alpha = 0
        self.beta = 0
        if self.sketch['football'] > 0:
            game_fair = self.sketch['game_fair']
            if game_fair < 0.25:
                self.alpha = 0.0
                self.beta = 0.0
            elif self.sketch['game_fair'] > 0.75:
                self.alpha = 1.0
                self.beta = 0.0
            else:
                self.alpha = 1.0
                self.beta = 1.0

    def __get_utility_for(self, play: PlayData):
        team_score = play.offense_team_score  # This only works because we are considering only offense
        opponent_score = play.defense_team_score  # This only works because we are considering only offense

        if team_score == 0 and opponent_score == 0:
            utility = 1.0
        else:
            adjusted_alpha = self.alpha
            adjusted_beta = self.beta

            if opponent_score == 0 and self.alpha == 1.0 and self.beta == 1.0:
                adjusted_alpha = 0.75
                adjusted_beta = 0.75

            utility = (team_score -
                       adjusted_alpha * (max(opponent_score - team_score, 0)) -
                       adjusted_beta * (max(team_score - opponent_score, 0))
                       ) / max(team_score, opponent_score)

        self.debug_info += (str(team_score) + ' - ' + str(opponent_score) + ' -> ' + str(utility))

        return utility

    def __get_perceived_probability_for__(self, play: PlayData):
        past = self.sketch['past']
        present = 1.0 - past
        positive_dev = self.sketch['positive']
        negative_dev = self.sketch['negative']
        coping = self.sketch['coping']

        historical_probability = present * play.win_probability + past * self.game.game_odds
        positive_negative_dev_effect = positive_dev * 0.2 - negative_dev + coping

        probability = historical_probability + positive_negative_dev_effect

        # For example:
        # eo = ((((1 - 0.5) * 0) + (0.5 * 0.7)) + 0.0 - (0 - 0)) # for my own team
        probability = min(1.0, max(0.0, probability))
        self.debug_info += '\nSeen win prob: ' + str(play.win_probability) + ', Odds: ' + str(self.game.game_odds)

        return probability

    def determine_utilities_for(self, play: PlayData):
        predicted_behavior = Behavior()

        predicted_behavior.utility = self.__get_utility_for(play)  # based on fair-scmidt we have utilities

        # Need eo for the play of the other team if we have time
        predicted_behavior.probability = self.__get_perceived_probability_for__(play)  # will be equal to the eo
        predicted_behavior.compute_expected_outcome(threshold=0.4)

        return predicted_behavior

    def watch_game(self, game):
        self.game = game

    def set_emotion_mode(self, new_emotion_model):
        self.emotion_model = new_emotion_model

    def get_emotion_for(self, play: PlayData):
        self.debug_info = play.play_description + '\n' + 'Predicted: '

        predicted_behavior = self.determine_utilities_for(play)

        self.debug_info += '\nStatistical Probability: ' + str(play.statistical_behavior.probability)
        self.debug_info += '\nPerceived Probability: ' + str(predicted_behavior.probability)
        self.debug_info += '\nActual Behavior: ' + str(play.is_complete)

        print(self.debug_info)

        # Compare here with statistical behavior
        return self.emotion_model.process(predicted_behavior=predicted_behavior,
                                          statistical_behavior=play.statistical_behavior,
                                          actual_play=play)


