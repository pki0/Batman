import json
import math

from cp_multiplier import cp_multiplier
from gamemaster_functions import *
from pvp_functions import *

# GameMaster Stuff
gamemaster_file = '../static/gamemaster.json'

# Read GamemasterFile
try:
    with open(gamemaster_file, 'r', encoding='utf-8') as f:
        gamemaster_data = json.loads(f.read())

except Exception as e:
    print('%s' % (repr(e)))
    # Pass to ignore if some files missing.
    pass

# Cut gamemaster_data
gamemaster_data = cut_gamemaster(gamemaster_data)

# Pokemon names stuff
locale_file = '../locales/pokemon.de.json'

# Read locales
try:
    with open(locale_file, 'r', encoding='utf-8') as f:
        pokemon_names = json.loads(f.read())
except Exception as e:
    print('%s' % (repr(e)))
    # Pass to ignore if some files missing.
    pass


# Create nice lists
# 1. Rankings only | 2. Rankings with  IVs
rankings_dict = {}
rankings_iv_dict = {}
for i in range(1,900):
    print("Process %s %%" % float((float(i)/9)))
    rankings_dict['pkmn_%s' % i] = []
    rankings_iv_dict['pkmn_%s' % i] = []

    bases = get_stats_from_gamemaster(i,gamemaster_data,pokemon_names)
    if bases == False:
        continue
    base_a = int(bases["pokemon_stats_a"])
    base_d = int(bases["pokemon_stats_d"])
    base_s = int(bases["pokemon_stats_s"])
    max_level_p, max_cp_p  = get_maximum_level(i, base_a, base_d, base_s, 0, 0, 0, 0, cp_multiplier)
    score_dict = dict()
    k = 1
    for iv0_a in range(0,16):
        for iv0_d in range(0,16):
            for iv0_s in range(0,16):
                max_level, cp_tmp  = get_maximum_level(i, base_a, base_d, base_s, iv0_a, iv0_d, iv0_s, 0, cp_multiplier)
                max_cpm  = cp_multiplier[str(max_level)]
                rank_val = math.pow(max_cpm,2)*(base_a+iv0_a)*(base_d+iv0_d)*math.floor(max_cpm*(base_s+iv0_s))
                score_dict[k] = {"score":rank_val, "iv0_a":iv0_a, "iv0_d":iv0_d, "iv0_s":iv0_s}
                k += 1

    sorted_score = sorted(score_dict.items(), key=lambda item: int(item[1]['score']))

    for j in reversed(sorted_score):
        rankings_dict['pkmn_%s' % i].append(j[1]["score"])
        rankings_iv_dict['pkmn_%s' % i].append(j)


# Store the shittah
with open('../static/pvp_rankings.json', 'w') as fp:
    json.dump(rankings_dict, fp)
with open('../static/pvp_iv_rankings.json', 'w') as fp:
    json.dump(rankings_iv_dict, fp)

print("Success")
