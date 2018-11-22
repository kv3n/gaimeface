import pandas as pd
from gamedatadump import *
from gameenums import *
from character import *
from behavior import *
from flask import Flask, request
app = Flask(__name__)


class GameData:
    def __make_game_dictionary__(self):
        successful_play_prob = {"0_0": 0,
                                "1_1": 0, "1_2": 0, "1_3": 0, "1_4": 0, "1_5": 0, "1_6": 0, "1_7": 0, "1_8": 0, "1_9": 0, "1_10": 0,
                                "2_1": 0, "2_2": 0, "2_3": 0, "2_4": 0, "2_5": 0, "2_6": 0, "2_7": 0, "2_8": 0, "2_9": 0, "2_10": 0,
                                "3_1": 0, "3_2": 0, "3_3": 0, "3_4": 0, "3_5": 0, "3_6": 0, "3_7": 0, "3_8": 0, "3_9": 0, "3_10": 0,
                                "4_1": 0, "4_2": 0, "4_3": 0, "4_4": 0, "4_5": 0, "4_6": 0, "4_7": 0, "4_8": 0, "4_9": 0, "4_10": 0}
        total_plays = {"0_0": 0,
                       "1_1": 0, "1_2": 0, "1_3": 0, "1_4": 0, "1_5": 0, "1_6": 0, "1_7": 0, "1_8": 0, "1_9": 0, "1_10": 0,
                       "2_1": 0, "2_2": 0, "2_3": 0, "2_4": 0, "2_5": 0, "2_6": 0, "2_7": 0, "2_8": 0, "2_9": 0, "2_10": 0,
                       "3_1": 0, "3_2": 0, "3_3": 0, "3_4": 0, "3_5": 0, "3_6": 0, "3_7": 0, "3_8": 0, "3_9": 0, "3_10": 0,
                       "4_1": 0, "4_2": 0, "4_3": 0, "4_4": 0, "4_5": 0, "4_6": 0, "4_7": 0, "4_8": 0, "4_9": 0, "4_10": 0}

        return successful_play_prob, total_plays

    def __update_game_dictionary__(self, success, total, cur_play: PlayData):
        if cur_play.down <= 3:
            total[cur_play.play_key] += 1
            if cur_play.yards > 0:
                success[cur_play.play_key] += 1
        elif cur_play.down == 4:
            if cur_play.play_type != PlayType.PUNT:
                total[cur_play.play_key] += 1

            if cur_play.yards >= cur_play.to_go:
                success[cur_play.play_key] += 1
            elif (cur_play.play_type == PlayType.FIELDGOAL) and (not cur_play.is_incomplete):
                success[cur_play.play_key] += 1

    def __init__(self, gameid, home_team, away_team, character_team):
        game_data_frame = pd.read_csv(play_by_play_data)

        # Fix bad play data
        game_data_frame['PlayType'].fillna('QUARTER', inplace=True)
        game_data_frame.loc[game_data_frame['Description'].str.contains('TWO-MINUTE'), 'PlayType'] = 'TWOMINUTE'
        game_data_frame['OffenseTeam'].fillna('NONE', inplace=True)

        is_nogood = game_data_frame['Description'].str.contains('NO GOOD')
        is_fieldgoal = game_data_frame['PlayType'].str.contains('FIELD GOAL')
        is_extrapoint = game_data_frame['PlayType'].str.contains('EXTRA POINT')

        game_data_frame.loc[is_nogood & (is_fieldgoal | is_extrapoint), 'IsIncomplete'] = 1

        self.game_data = game_data_frame.loc[(game_data_frame['GameId'] == gameid)]
        self.home_team = home_team
        self.away_team = away_team

        # Make the play dictionary
        successful_play_prob, total_plays = self.__make_game_dictionary__()

        # Sort game data for chronological ordering
        self.game_data = self.game_data.sort_values(by=['Quarter', 'Minute', 'Second', 'PlayType'],
                                                    ascending=[True, False, False, True])

        self.play_data = []
        for _, game_play_row in self.game_data.iterrows():
            play = PlayData(game_play_row)
            if play.offense_team != character_team:
                continue

            play.actual_behavior = random.randint(0,1) # to test basic emotion model

            play.calculate_statistical_behavior(successful_play_prob, total_plays)
            self.__update_game_dictionary__(successful_play_prob, total_plays, play)

            self.play_data.append(play)

    def print_game_data(self):
        [print(play) for play in self.play_data]


character = None
game_data = None


@app.route("/consume_play")
def consume_play():
    play_id = int(request.args.get('playid'))

    play = game_data.play_data[play_id]
    emotion_label = character.get_emotion_for(play)

    play_reaction = {'emotion_label': emotion_label}
    return str(play_reaction)


@app.route("/init_game")
def init_game():
    global character
    global game_data
    character_name = request.args.get('name')
    discrete_model = SchererModel(4)  # Once we have different emotion models substitute a model here
    character = Character(character_name, discrete_model)
    game_data = GameData(2018100710, Team.SF, Team.ARI, Team.SF)  # Arizona vs 49ers

    result = {"num_plays": len(game_data.play_data)}

    return str(result)


def main():
    #app.run(debug=True, port=5000)  # run app in debug mode on port 5000
    game_data = GameData(2018100710, Team.SF, Team.ARI, Team.SF)  # Arizona vs 49ers


if __name__ == "__main__":
    main()
