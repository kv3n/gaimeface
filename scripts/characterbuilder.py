import json
from gamedatadump import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Sketch:
    def __init__(self):
        self.sketch_file = 'temp'
        self.sketch = dict()
        self.sketch['football'] = 0.0

    def update_football_love(self, value):
        self.sketch['football'] = value / 100.0

    def build_character_sketch(self):
        with open(self.sketch_file + '.json', 'w') as outfile:
            json.dump(self.sketch, outfile)

    def set_file_name(self, name):
        self.sketch_file = name

# TODO: Add code to generate the sketch here

def create_labeled_slider(label_name, slider_callback=None):
    h_layout = QHBoxLayout()
    h_layout.addWidget(QLabel(label_name))
    slider = QSlider(Qt.Horizontal)
    h_layout.addWidget(slider)
    slider.valueChanged.connect(slider_callback)

    return h_layout

def create_button_with_name(button_name, button_callback=None):
    button = QPushButton(button_name)
    button.clicked.connect(button_callback)

    return button

def create_labeled_input_text(label_name, text_change_callback=None):
    h_layout = QHBoxLayout()
    h_layout.addWidget(QLabel(label_name))
    textbox = QLineEdit()
    textbox.textChanged.connect(text_change_callback)
    h_layout.addWidget(textbox)
    return h_layout


# Build character this way
active_sketch = Sketch()

app = QApplication([])
window = QWidget()
v_layout = QVBoxLayout()
v_layout.addWidget(QLabel('Character Builder'))
v_layout.addLayout(create_labeled_input_text('Character Name', text_change_callback=active_sketch.set_file_name))
v_layout.addLayout(create_labeled_slider('Football Love', slider_callback=active_sketch.update_football_love))
v_layout.addWidget(create_button_with_name('Build Character', button_callback=active_sketch.build_character_sketch))
window.setLayout(v_layout)
window.show()
app.exec()

#build_character_sketch('kishore')
