import random


class Behavior:
    def __init__(self):
        self.expected_outcome = 0 # player expected it to succeed or fail
        self.utility = 0.0 # The utility of that play being successful
        self.probability = 0.0 # The probability of that play being successful

    def __str__(self):
        return ('Expected: ' + str(self.expected_outcome) + ' ' + 'Utility: ' + str(self.utility) + ' ' 
        + 'Probability: ' + str(self.probability))

class EmotionModel:
    def __init__(self, seed = -1):
        self.seed = -1
        random.seed(self.seed)

    def process(self, predicted_behavior, statistical_behavior, actual_behavior):
        # Do Emotion Calculation here
        return random.randint(0, 5)

class DummyModel(EmotionModel):
    def __init__(self, seed = -1):
        EmotionModel.__init__(self, seed)
        self.NEUTRAL = 0
        self.HAPPY = 1
        self.SAD = 2

    def process(self, predicted_behavior, statistical_behavior, actual_behavior):
        # Do Emotion Calculation here
        emotion = 2.5
        # print('Predicted: ' + str(predicted_behavior))
        # print('Statistical: ' + str(statistical_behavior))
        # print('Actual: ' + str(actual_behavior))
        if (predicted_behavior.expected_outcome == actual_behavior):
            if (predicted_behavior.probability < 0.5): # expected outcome had low probability but it is same as character wanted
                emotion = emotion + 0.5
            else:
                emotion = emotion + 0.25
            if (predicted_behavior.utility < 0.5): # expected outcome had low utility but it is same as character wanted
                emotion = emotion + 0.25
            else:
                emotion = emotion + 0.5            
        else:
            if (predicted_behavior.probability < 0.5): # expected outcome had low probability and it didn't happen as character wanted
                emotion = emotion - 0.25
            else:
                emotion = emotion - 0.5
            if (predicted_behavior.utility < 0.5): # expected outcome had low utility and it didn't happen as character wanted
                emotion = emotion - 0.25
            else:
                emotion = emotion - 0.5

        if (statistical_behavior.expected_outcome == actual_behavior):
            if (statistical_behavior.probability < 0.5): # expected outcome had low probability but it is same as character wanted
                emotion = emotion + 0.5
            else:
                emotion = emotion + 0.25
            if (statistical_behavior.utility < 0.5): # expected outcome had low utility but it is same as character wanted
                emotion = emotion + 0.25
            else:
                emotion = emotion + 0.5            
        else:
            if (statistical_behavior.probability < 0.5): # expected outcome had low probability and it didn't happen as character wanted
                emotion = emotion - 0.25
            else:
                emotion = emotion - 0.5
            if (statistical_behavior.utility < 0.5): # expected outcome had low utility and it didn't happen as character wanted
                emotion = emotion - 0.25
            else:
                emotion = emotion - 0.5

        if (statistical_behavior.expected_outcome != predicted_behavior.expected_outcome and predicted_behavior.expected_outcome == actual_behavior):
            emotion = emotion + 0.5

        if (statistical_behavior.expected_outcome == predicted_behavior.expected_outcome and predicted_behavior.expected_outcome != actual_behavior):
            emotion = emotion - 0.5

        if (emotion > 2.5):
            return self.HAPPY
        elif (emotion < 2.5):
            return self.SAD
        else:
            return self.NEUTRAL
