from behavior import *
from playchart import *
from gamedatadump import *
import json


class Character:
    def __init__(self, sketch_file, emotion_model):
        self.emotion_model = emotion_model

        self.sketch = {}
        with open(data_loc + sketch_file + '.json') as sketch_data:
            self.sketch = json.load(sketch_data)

    def determine_utilities_for(self, play):
        predicted_behavior = Behavior()

        predicted_behavior.expected_outcome = random.randint(0,1) # to test basic emotion model
        predicted_behavior.utility = random.uniform(0,1) # to test basic emotion model
        predicted_behavior.probability = random.uniform(0,1) # to test basic emotion model

        return predicted_behavior

    def set_emotion_mode(self, new_emotion_model):
        self.emotion_model = new_emotion_model

    def get_emotion_for(self, play):
        predicted_behavior = self.determine_utilities_for(play)

        # Compare here with statistical behavior
        return self.emotion_model.process(predicted_behavior=predicted_behavior,
                                          statistical_behavior=play.statistical_behavior,
                                          actual_behavior=play.actual_behavior)


