import json
from gamedatadump import *


def build_character_sketch(sketch_file):
    sketch = dict()
    sketch['football'] = 0.8
    sketch['external'] = 0.4
    sketch['plays'] = 0.7

    with open(data_loc + sketch_file + '.json', 'w') as outfile:
        json.dump(sketch, outfile)

# TODO: Add code to generate the sketch here

# Build character this way
#build_character_sketch('kishore')
