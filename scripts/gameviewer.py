import pandas as pd
from gamedatadump import *
from gameenums import *
from datetime import timedelta


class PlayData:
    def __init__(self):
        self.quarter = 1
        self.offense_team = Team.NONE
        self.defense_team = Team.NONE
        self.time_left = timedelta(minutes=0, seconds=0)
        self.play_type = PlayType.NONE
        self.play_description = ''

    def is_active_play(self):
        return (self.play_type != PlayType.TIMEOUT and
                self.play_type != PlayType.QUARTER and
                self.play_type != PlayType.TWOMINUTE)

    def __str__(self):
        return (str(self.quarter) + ' ' + str(self.time_left) + ' ' + str(self.play_type) + ' ' +
                str(self.offense_team) + ' ' + str(self.defense_team) + '\t' +
                self.play_description)


class GameData:
    def __init__(self, gameid, home_team, away_team):
        game_data_frame = pd.read_csv(play_by_play_data)

        # Fix bad play data
        game_data_frame['PlayType'].fillna('QUARTER', inplace=True)
        game_data_frame.loc[game_data_frame['Description'].str.contains('TWO-MINUTE'), 'PlayType'] = 'TWOMINUTE'
        game_data_frame['OffenseTeam'].fillna('NONE', inplace=True)

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

            if play.is_active_play():
                play.offense_team = Team(game_play_row['OffenseTeam'])
                play.defense_team = Team(game_play_row['DefenseTeam'])

            self.play_data.append(play)

    def print_game_data(self):
        [print(play) for play in self.play_data]


def main():
    game_data = GameData(2018100710, Team.SF, Team.ARI)  # Arizona vs 49ers
    game_data.print_game_data()


if __name__ == "__main__":
    main()
