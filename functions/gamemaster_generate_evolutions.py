import json
import logging

from gamemaster_functions import *

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


evolution_dict = {}
for i in range(1,810):
    evolution_dict[i] = get_evolutions_from_gamemaster(i,gamemaster_data,pokemon_names)


base_stats_file_name = '../static/pokemon_evolutions.json'
with open(base_stats_file_name, 'w') as fp:
    json.dump(evolution_dict, fp)

logger.info("Success")