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

detailed_files = True

########################


logging.basicConfig(
    format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)-8s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


# GameMaster stuff
gamemaster_file = '../static/gamemaster.json'
try:
    with open(gamemaster_file, 'r', encoding='utf-8') as f:
        gamemaster_data = json.loads(f.read())

except Exception as e:
    logger.error('%s' % (repr(e)))
    logger.error('%s not found' % gamemaster_file)
    sys.exit(1)

# Pokemon names stuff
locale_file = '../locales/pokemon.de.json'
try:
    with open(locale_file, 'r', encoding='utf-8') as f:
        pokemon_names = json.loads(f.read())
except Exception as e:
    logger.error('%s' % (repr(e)))
    logger.error('%s not found' % locale_file)
    sys.exit(1)

# Pokemon base stats stuff
base_stats_file = '../static/pokemon_base_stats.json'
try:
    with open(base_stats_file, 'r', encoding='utf-8') as f:
        pokemon_base_stats = json.loads(f.read())
except Exception as e:
    logger.error('%s' % (repr(e)))
    logger.error('%s not found' % base_stats_file)
    sys.exit(1)



# Cut gamemaster_data
gamemaster_data = cut_gamemaster(gamemaster_data)

# Create nice lists
def generate_lists(league_cp, maximum_level, cp_multiplier, detailed_files, processname):
    # 1. Rankings only | 2. Rankings with  IVs
    sim_level = 0
    rankings_dict = {}
    rankings_iv_dict = {}
    for i in range(1,810):
        logger.info("%s: %.2f %% done." % (processname, float((float(i)/8)))) if float((float(i)/8)) % 5 == 0 else None
        rankings_dict['pkmn_%s' % i] = []
        rankings_iv_dict['pkmn_%s' % i] = []

        bases = pokemon_base_stats[str(i)]
        if not bases:
            continue
        base_a = int(bases["baseAttack"])
        base_d = int(bases["baseDefense"])
        base_s = int(bases["baseStamina"])
        score_dict = dict()
        k = 1
        for iv_attack in range(0,16):
            for iv_defense in range(0,16):
                for iv_stamina in range(0,16):
                    pvp_level, pvp_cp, pvp_rank = get_pvp_values(base_a, base_d, base_s, iv_attack, iv_defense, iv_stamina, league_cp, cp_multiplier, sim_level)
                    score_dict[k] = {"pvpScore":pvp_rank, "ivAttack":iv_attack, "ivDefense":iv_defense, "ivStamina":iv_stamina}
                    k += 1

        sorted_score = sorted(score_dict.items(), key=lambda item: int(item[1]['pvpScore']))

        for j in reversed(sorted_score):
            rankings_dict['pkmn_%s' % i].append(j[1]["pvpScore"])
            if detailed_files == True:
                rankings_iv_dict['pkmn_%s' % i].append(j)

    logger.info("%s: Saving files..." % processname)
    store_lists_as_json(league_cp, maximum_level, rankings_dict, rankings_iv_dict, detailed_files)
    logger.info("%s: Success" % processname)
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
    p = multiprocessing.Process(target=generate_lists, args=(1500, 40, cp_multiplier_40, detailed_files, "File 1",))
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=generate_lists, args=(1500, 41, cp_multiplier_41, detailed_files, "File 2",))
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=generate_lists, args=(2500, 40, cp_multiplier_40, detailed_files, "File 3",))
    processes.append(p)
    p.start()
    p = multiprocessing.Process(target=generate_lists, args=(2500, 41, cp_multiplier_41, detailed_files, "File 4",))
    processes.append(p)
    p.start()

    for process in processes:
        process.join()
