from behavior import *
from playchart import *


class Character:
    def __init__(self, emotion_model):
        self.sketch = {}
        self.emotion_model = emotion_model

    def determine_utilities_for(self, play):
        predicted_behavior = Behavior()
        return predicted_behavior

    def set_emotion_mode(self, new_emotion_model):
        self.emotion_model = new_emotion_model

    def get_emotion_for(self, play):
        predicted_behavior = self.determine_utilities_for(play)

        # Compare here with statistical behavior
        return self.emotion_model.process(predicted_behavior=predicted_behavior,
                                          statistical_behavior=play.statistical_behavior)


