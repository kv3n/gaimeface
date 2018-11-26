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
            elif (cur_play.play_type == PlayType.FIELDGOAL) and cur_play.is_complete:
                success[cur_play.play_key] += 1

    def __init__(self, gameid, home_team, away_team, character_team):
        game_data_frame = pd.read_csv(play_by_play_data)

        # Fix bad play data
        game_data_frame['down'].fillna(0, inplace=True)
        game_data_frame['PosTeamScore'].fillna(0, inplace=True)
        game_data_frame['DefTeamScore'].fillna(0, inplace=True)
        game_data_frame['FieldGoalDistance'].fillna(0, inplace=True)

        self.game_data = game_data_frame.loc[(game_data_frame['GameID'] == gameid)]
        self.home_team = home_team
        self.away_team = away_team

        # Make the play dictionary
        successful_play_prob, total_plays = self.__make_game_dictionary__()

        # Sort game data for chronological ordering
        self.game_data = self.game_data.sort_values(by=['qtr', 'TimeUnder', 'TimeSecs'],
                                                    ascending=[True, False, False])

        self.play_data = []
        for _, game_play_row in self.game_data.iterrows():
            play = PlayData(game_play_row)
            if play.offense_team != character_team:
                continue

            play.calculate_statistical_behavior(successful_play_prob, total_plays)
            self.__update_game_dictionary__(successful_play_prob, total_plays, play)

            self.play_data.append(play)

        self.game_odds = self.play_data[0].win_probability

    def print_game_data(self):
        [print(play) for play in self.play_data]


character = None
game_data = None


@app.route("/consume_play")
def consume_play():
    play_id = int(request.args.get('playid'))

    play: PlayData = game_data.play_data[play_id]
    emotion_label = character.get_emotion_for(play)
    print('Requested Emotion: ' + str(emotion_label['emotion']) + ' with intensity: ' + str(emotion_label['intensity']))

    play_reaction = {'emotion_label': emotion_label['emotion'], 'intensity': emotion_label['intensity'], 'play_desc': play.play_description}
    return str(play_reaction)


@app.route("/init_game")
def init_game():
    global character
    global game_data
    character_name = request.args.get('name')
    discrete_model = SchererModel(4)  # Once we have different emotion models substitute a model here
    character = Character(character_name, discrete_model)
    game_data = GameData(2017122409, Team.SF, Team.JAX, Team.SF)  # Jacksonville @ 49ers
    character.watch_game(game_data)

    result = {"num_plays": len(game_data.play_data)}

    return str(result)


def main():
    app.run(debug=True, port=5000)  # run app in debug mode on port 5000

    """
    game_data = GameData(2017122409, Team.SF, Team.JAX, Team.SF)  # Jaguars @ 49ers
    discrete_model = SchererModel(4)  # Once we have different emotion models substitute a model here
    character = Character('kishore', discrete_model)
    character.watch_game(game_data)
    for play in game_data.play_data:
        print(play.play_description)
        emotion_label = character.get_emotion_for(play)
        print(emotion_label)
    """


if __name__ == "__main__":
    main()
