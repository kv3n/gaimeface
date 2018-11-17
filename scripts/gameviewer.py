import pandas as pd
from gamedatadump import *
from gameenums import *
from character import *
from behavior import *
from flask import Flask, request
app = Flask(__name__)

from datetime import timedelta


class GameData:
    def __init__(self, gameid, home_team, away_team):
        game_data_frame = pd.read_csv(play_by_play_data)

        # Fix bad play data
        game_data_frame['PlayType'].fillna('QUARTER', inplace=True)
        game_data_frame.loc[game_data_frame['Description'].str.contains('TWO-MINUTE'), 'PlayType'] = 'TWOMINUTE'
        game_data_frame['OffenseTeam'].fillna('NONE', inplace=True)

        is_nogood = game_data_frame['Description'].str.contains('NO GOOD')
        is_fieldgoal = game_data_frame['PlayType'].str.contains('FIELD GOAL')
        is_extrapoint = game_data_frame['PlayType'].str.contains('EXTRA POINT')

        game_data_frame.loc[is_nogood & (is_fieldgoal | is_extrapoint), 'IsIncomplete'] = 1

        self.game_data = game_data_frame.loc[game_data_frame['GameId'] == gameid]
        self.home_team = home_team
        self.away_team = away_team

        # Sort game data for chronological ordering
        self.game_data = self.game_data.sort_values(by=['Quarter', 'Minute', 'Second', 'PlayType'],
                                                    ascending=[True, False, False, True])

        self.play_data = []
        for _, game_play_row in self.game_data.iterrows():
            play = PlayData()
            play.quarter = game_play_row['Quarter']
            play.time_left = timedelta(minutes=game_play_row['Minute'], seconds=game_play_row['Second'])
            play.play_type = PlayType(game_play_row['PlayType'])
            play.play_description = game_play_row['Description']

            play.actual_behavior = random.randint(0,1) # to test basic emotion model

            if play.is_active_play():
                play.offense_team = Team(game_play_row['OffenseTeam'])
                play.defense_team = Team(game_play_row['DefenseTeam'])

            play.calculate_statistical_behavior()
            self.play_data.append(play)

    def print_game_data(self):
        [print(play) for play in self.play_data]


character = None
game_data = None


@app.route("/consume_play")
def consume_play():
    play_id = int(request.args.get('playid'))

    emotion_label = character.get_emotion_for(game_data.play_data[play_id])

    play_reaction = {'emotion_label': emotion_label}
    return str(play_reaction)


@app.route("/init_game")
def init_game():
    global character
    global game_data
    character_name = request.args.get('name')
    discrete_model = DummyModel(4)  # Once we have different emotion models substitute a model here
    character = Character(character_name, discrete_model)
    game_data = GameData(2018100710, Team.SF, Team.ARI)  # Arizona vs 49ers

    result = {"num_plays": len(game_data.play_data)}

    return str(result)


def main():
    #app.run(debug=True, port=5000)  # run app in debug mode on port 5000
    game_data = GameData(2018100710, Team.SF, Team.ARI)  # Arizona vs 49ers

if __name__ == "__main__":
    main()
