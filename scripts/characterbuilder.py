import json
from gamedatadump import *
from gameenums import Team
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


def create_labeled_slider(label_name, slider_callback):
    h_layout = QHBoxLayout()
    h_layout.addWidget(QLabel(label_name))

    slider = QSlider(Qt.Horizontal)
    slider.valueChanged.connect(slider_callback)
    h_layout.addWidget(slider)

    return h_layout, slider


def create_button_with_name(button_name, button_callback):
    button = QPushButton(button_name)
    button.clicked.connect(button_callback)

    return button


def create_labeled_input_text(label_name, text_change_callback):
    h_layout = QHBoxLayout()
    h_layout.addWidget(QLabel(label_name))
    textbox = QLineEdit()
    textbox.textChanged.connect(text_change_callback)
    h_layout.addWidget(textbox)
    return h_layout, textbox


def create_labeled_combo(label_name, enum, combo_box_callback):
    h_layout = QHBoxLayout()
    h_layout.addWidget(QLabel(label_name))
    combo = QComboBox()
    for e in enum:
        combo.addItem(str(e), e)
    h_layout.addWidget(combo)
    combo.currentIndexChanged.connect(combo_box_callback)

    return h_layout, combo


class Sketch:
    def __init__(self):
        self.sketch_file = 'temp'
        self.sketch = dict()
        self.widget = dict()
        self.window = QWidget()

        self.__build_gui__()

    def __build_gui__(self):
        # Character build label
        v_layout = QVBoxLayout()
        v_layout.addWidget(QLabel('Character Builder'))

        # File name for saving / loading
        layout, text_edit = create_labeled_input_text('Character Name',
                                                      text_change_callback=self.set_file_name)
        v_layout.addLayout(layout)

        # Build parameters
        layout, football_slider = create_labeled_slider('Football', slider_callback=self.update_football_love)
        v_layout.addLayout(layout)
        self.add_dictionary_item('football', 0.0, football_slider)

        layout, influence_slider = create_labeled_slider('Influence', slider_callback=self.update_influence)
        v_layout.addLayout(layout)
        self.add_dictionary_item('influence', 0.0, influence_slider)

        layout, positive_slider = create_labeled_slider('Positive', slider_callback=self.update_positive)
        v_layout.addLayout(layout)
        self.add_dictionary_item('positive', 0.0, positive_slider)

        layout, negative_slider = create_labeled_slider('Negative', slider_callback=self.update_negative)
        v_layout.addLayout(layout)
        self.add_dictionary_item('negative', 0.0, negative_slider)

        layout, coping_slider = create_labeled_slider('Coping', slider_callback=self.update_coping)
        v_layout.addLayout(layout)
        self.add_dictionary_item('coping', 0.0, coping_slider)

        layout, reaction_slider = create_labeled_slider('Reaction', slider_callback=self.update_reaction)
        v_layout.addLayout(layout)
        self.add_dictionary_item('reaction', 0.0, reaction_slider)

        layout, past_slider = create_labeled_slider('Past', slider_callback=self.update_past)
        v_layout.addLayout(layout)
        self.add_dictionary_item('past', 0.0, past_slider)

        layout, game_fair_slider = create_labeled_slider('Game Fair', slider_callback=self.update_game_fair)
        v_layout.addLayout(layout)
        self.add_dictionary_item('game_fair', 0.0, game_fair_slider)

        layout, game_play_slider = create_labeled_slider('Playing', slider_callback=self.update_playing)
        v_layout.addLayout(layout)
        self.add_dictionary_item('playing', 0.0, game_play_slider)

        layout, fav_players_text = create_labeled_input_text('Favs', text_change_callback=self.update_favs)
        v_layout.addLayout(layout)
        self.add_dictionary_item('favs', '', fav_players_text)

        layout, disliked_players_text = create_labeled_input_text('Dislikes', text_change_callback=self.update_dislikes)
        v_layout.addLayout(layout)
        self.add_dictionary_item('dislikes', '', disliked_players_text)

        layout, fav_team_combo = create_labeled_combo('Fav Team', Team, combo_box_callback=self.update_fav_team_combo)
        v_layout.addLayout(layout)
        self.add_dictionary_item('fav_team', str(Team.SF).lstrip('Team.'), fav_team_combo)

        # Build / Load Character
        h_layout = QHBoxLayout()
        h_layout.addWidget(create_button_with_name('Build Character',
                                                   button_callback=self.build_character_sketch))
        h_layout.addWidget(create_button_with_name('Load Character',
                                                   button_callback=self.load_file))
        v_layout.addLayout(h_layout)

        self.window.setLayout(v_layout)
        self.window.show()

    def add_dictionary_item(self, key, default_val, widget):
        self.sketch[key] = default_val
        self.widget[key] = widget

    def update_football_love(self, value):
        self.sketch['football'] = value / 100.0

    def update_influence(self, value):
        self.sketch['influence'] = value / 100.0

    def update_positive(self, value):
        self.sketch['positive'] = value / 100.0

    def update_negative(self, value):
        self.sketch['negative'] = value / 100.0

    def update_coping(self, value):
        self.sketch['coping'] = value / 100.0

    def update_reaction(self, value):
        self.sketch['reaction'] = value / 100.0

    def update_past(self, value):
        self.sketch['past'] = value / 100.0

    def update_game_fair(self, value):
        self.sketch['game_fair'] = value / 100.0

    def update_playing(self, value):
        self.sketch['playing'] = value / 100.0

    def update_favs(self, favs):
        fav_players = favs.split(',')
        fav_players = [fav_player.strip() for fav_player in fav_players]
        self.sketch['favs'] = fav_players

    def update_dislikes(self, dislikes):
        disliked_players = dislikes.split(',')
        disliked_players = [disliked_player.strip() for disliked_player in disliked_players]
        self.sketch['dislikes'] = disliked_players

    def update_fav_team_combo(self, fav_team_index):
        enum_val = str(list(Team)[fav_team_index]).lstrip('Team.')
        self.sketch['fav_team'] = enum_val

    def build_character_sketch(self):
        with open(self.sketch_file + '.json', 'w') as outfile:
            json.dump(self.sketch, outfile)

    def set_file_name(self, name):
        self.sketch_file = name

    def load_file(self):
        with open(self.sketch_file + '.json', 'r') as infile:
            self.sketch = json.loads(infile.read())

        for key, value in self.sketch.items():
            if type(self.widget[key]) is QSlider:
                self.widget[key].setValue(int(value * 100.0))
            elif type(self.widget[key]) is QLineEdit:
                self.widget[key].setText(', '.join(value))
            elif type(self.widget[key]) is QComboBox:
                if key == 'fav_team':
                    enum_value = Team(value)
                    self.widget[key].setCurrentIndex(list(Team).index(enum_value))

        self.window.repaint()


app = QApplication([])

# Build character this way
active_sketch = Sketch()

app.exec()