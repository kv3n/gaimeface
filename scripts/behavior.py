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


class SchererModel(EmotionModel):
    def __init__(self, seed = -1):
        EmotionModel.__init__(self, seed)
        self.NEUTRAL = 0
        self.HAPPY = 1
        self.SAD = 2
        self.FEAR = 3
        self.ANGER = 4

    def process(self, predicted_behavior, statistical_behavior, actual_behavior):
        joy = 0
        fear = 0
        anger = 0
        sadness = 0
        if (actual_behavior == 1):
            if (predicted_behavior.expected_outcome == actual_behavior):
                joy = predicted_behavior.utility * (1 - predicted_behavior.probability)
                if (predicted_behavior.expected_outcome == statistical_behavior.expected_outcome):
                    if (predicted_behavior.probability > 0.5 or statistical_behavior.probability > 0.5):
                        joy = joy - ((1 - abs(predicted_behavior.probability - statistical_behavior.probability)) * (1 - predicted_behavior.utility) * joy)
                else:
                    if (statistical_behavior.probability > predicted_behavior.probability):
                        if (predicted_behavior.probability > 0.5 or statistical_behavior.probability > 0.5):
                            joy = joy + (predicted_behavior.utility * joy)
                        else:
                            joy = joy + (statistical_behavior.probability * predicted_behavior.utility * joy)
                    else:
                        if (predicted_behavior.probability > 0.5 or statistical_behavior.probability > 0.5):
                            joy = joy + ((1 - abs(predicted_behavior.probability - statistical_behavior.probability)) * (predicted_behavior.utility) * joy)
            else:
                joy = predicted_behavior.utility * predicted_behavior.probability
                if (predicted_behavior.expected_outcome == statistical_behavior.expected_outcome):
                    if (predicted_behavior.probability > 0.5 or statistical_behavior.probability > 0.5):
                        joy = joy + (max(predicted_behavior.probability, statistical_behavior.probability)) * (predicted_behavior.utility) * joy
                else:
                    if (statistical_behavior.probability > predicted_behavior.probability):
                        if (predicted_behavior.probability > 0.5 or statistical_behavior.probability > 0.5):
                            joy = joy + (predicted_behavior.utility * joy)
                        else:
                            joy = joy + (statistical_behavior.probability * predicted_behavior.utility * joy)
                    else:
                        if (predicted_behavior.probability > 0.5 or statistical_behavior.probability > 0.5):
                            joy = joy + ((1 - abs(predicted_behavior.probability - statistical_behavior.probability)) * (predicted_behavior.utility) * joy)
        else:
            if (predicted_behavior.expected_outcome != actual_behavior):
                fear = predicted_behavior.utility * (1 - predicted_behavior.probability)
                anger = predicted_behavior.utility * predicted_behavior.probability
                sadness = predicted_behavior.utility * predicted_behavior.probability
                if (predicted_behavior.expected_outcome != statistical_behavior.expected_outcome):
                    if (predicted_behavior.probability < 0.5 and statistical_behavior.probability > 0.5):
                        fear = fear - (abs(statistical_behavior.probability - predicted_behavior.probability) * (1 - predicted_behavior.utility) * fear)
                        anger = anger - (abs(statistical_behavior.probability - predicted_behavior.probability) * (1 - predicted_behavior.utility) * anger)
                        sadness = sadness - (abs(statistical_behavior.probability - predicted_behavior.probability) * (1 - predicted_behavior.utility) * sadness)
                else:
                    if (predicted_behavior.probability > 0.5 or statistical_behavior.probability > 0.5):
                        fear = fear + (max(statistical_behavior.probability, predicted_behavior.probability) * (predicted_behavior.utility) * fear)
                        anger = anger + (max(statistical_behavior.probability, predicted_behavior.probability) * (predicted_behavior.utility) * anger)
            else:
                fear = predicted_behavior.utility * (1 - predicted_behavior.probability)
                sadness = predicted_behavior.utility * predicted_behavior.probability


        if (joy > fear and joy > anger and joy > sadness):
            return {'emotion':self.HAPPY, 'intensity':joy}
        elif (fear > joy and fear > anger and fear > sadness):
            return {'emotion':self.FEAR, 'intensity':fear}
        elif (anger > fear and anger > joy and anger > sadness):
            return {'emotion':self.ANGER, 'intensity':anger}
        elif (sadness > fear and sadness > anger and sadness > joy):
            return {'emotion':self.SAD, 'intensity':sadness}
        elif (sadness == anger and sadness > fear and sadness > joy and sadness < 0.7):
            return {'emotion':self.SAD, 'intensity':sadness}
        elif (sadness == anger and sadness > fear and sadness > joy and sadness >= 0.7):
            return {'emotion':self.ANGER, 'intensity':anger}
        else:
            return self.NEUTRAL        

