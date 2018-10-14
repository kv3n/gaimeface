import random


class Behavior:
    def __init__(self):
        self.utility = 0
        self.probability = 0


class EmotionModel:
    def __init__(self, seed = -1):
        self.seed = -1
        random.seed(self.seed)

    def process(self, predicted_behavior, statistical_behavior):
        # Do Emotion Calculation here
        return random.randint(0, 5)
