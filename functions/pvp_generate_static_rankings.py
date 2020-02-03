'''
Generates static ranking files.
Check settings for detailed files. You can use them for other projects.
Batman doesn't need them.

Filesize is large: 50 MB for base files / 200 MB for detailed files!
Last change: 02.02.2020
'''

import json
import logging
import math
import multiprocessing
import sys

from cp_multiplier import *
from gamemaster_functions import *
from pvp_functions import *





####### SETTINGS #######

detailed_files = False

########################


logging.basicConfig(
    format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)-8s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# GameMaster Stuff
gamemaster_file = '../static/gamemaster.json'

# Read GamemasterFile
try:
    with open(gamemaster_file, 'r', encoding='utf-8') as f:
        gamemaster_data = json.loads(f.read())

except Exception as e:
    logger.error('%s' % (repr(e)))
    logger.error('%s not found' % gamemaster_file)
    sys.exit(1)

# Cut gamemaster_data
gamemaster_data = cut_gamemaster(gamemaster_data)

# Pokemon names stuff
locale_file = '../locales/pokemon.de.json'

# Read locales
try:
    with open(locale_file, 'r', encoding='utf-8') as f:
        pokemon_names = json.loads(f.read())
except Exception as e:
    logger.error('%s' % (repr(e)))
    logger.error('%s not found' % locale_file)
    sys.exit(1)


# Create nice lists
def generate_lists(league_cp, maximum_level, cp_multiplier, detailed_files):
    # 1. Rankings only | 2. Rankings with  IVs
    rankings_dict = {}
    rankings_iv_dict = {}
    for i in range(1,810):
        logger.info("Process: %.2f %% done." % float((float(i)/8))) if float((float(i)/8)) % 5 == 0 else None
        rankings_dict['pkmn_%s' % i] = []
        rankings_iv_dict['pkmn_%s' % i] = []

        bases = get_stats_from_gamemaster(i,gamemaster_data,pokemon_names)
        if bases == False:
            continue
        base_a = int(bases["baseAttack"])
        base_d = int(bases["baseDefense"])
        base_s = int(bases["baseStamina"])
        score_dict = dict()
        k = 1
        for iv0_a in range(0,16):
            for iv0_d in range(0,16):
                for iv0_s in range(0,16):
                    max_level, cp_tmp  = get_maximum_level(i, base_a, base_d, base_s, iv0_a, iv0_d, iv0_s, league_cp, cp_multiplier)
                    max_cpm  = cp_multiplier[str(max_level)]
                    rank_val = calculate_rank(base_a, base_d, base_s, iv0_a, iv0_d, iv0_s, max_cpm)
                    score_dict[k] = {"score":rank_val, "iv0_a":iv0_a, "iv0_d":iv0_d, "iv0_s":iv0_s}
                    k += 1

        sorted_score = sorted(score_dict.items(), key=lambda item: int(item[1]['score']))

        for j in reversed(sorted_score):
            rankings_dict['pkmn_%s' % i].append(j[1]["score"])
            if detailed_files == True:
                rankings_iv_dict['pkmn_%s' % i].append(j)

    logger.info("Saving files...")
    store_lists_as_json(league_cp, maximum_level, rankings_dict, rankings_iv_dict, detailed_files)
    logger.info("Success")
    return
    
def store_lists_as_json(league_cp, maximum_level, rankings_dict, rankings_iv_dict, detailed_files):
    # Store the shittah
    file_name = '../static/pvp_rankings_%s_level_%s.json' % (league_cp, maximum_level)
    file_name_iv = '../static/pvp_iv_rankings_%s_level_%s.json' % (league_cp, maximum_level)

    with open(file_name, 'w') as fp:
        json.dump(rankings_dict, fp)
    if detailed_files == True:
        with open(file_name_iv, 'w') as fp:
            json.dump(rankings_iv_dict, fp)



# Call functions
logger.info("Starting... Updating status every 5%.")

if __name__ == '__main__':

    processes = []
    p = multiprocessing.Process(target=generate_lists, args=(1500, 40, cp_multiplier_40, detailed_files,))
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=generate_lists, args=(1500, 41, cp_multiplier_41, detailed_files,))
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=generate_lists, args=(2500, 40, cp_multiplier_40, detailed_files,))
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=generate_lists, args=(2500, 41, cp_multiplier_41, detailed_files,))
    processes.append(p)
    p.start()
        
    for process in processes:
        process.join()
