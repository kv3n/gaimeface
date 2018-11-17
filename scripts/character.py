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

    def determine_utilities_for(self, play):
        predicted_behavior = Behavior()

        predicted_behavior.expected_outcome = random.randint(0,1) # if our team we want this to be one
        predicted_behavior.utility = random.uniform(0,1) # based on fair-scmidt we have utilities

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


