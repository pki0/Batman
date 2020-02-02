import math
import json
import time

from functions.pvp_functions import *
from functions.gamemaster_functions import *
from static.cp_multiplier import cp_multiplier

with open('static/gamemaster.json', 'r', encoding='utf-8') as f:
    gamemaster_data = json.loads(f.read())

with open('static/pvp_rankings.json', 'r', encoding='utf-8') as f:
    ranking_data = json.loads(f.read())

with open('locales/pokemon.de.json', 'r', encoding='utf-8') as f:
    pokemon_names = json.loads(f.read())


gm = cut_gamemaster(gamemaster_data)

# Try EVEEEEEEEEEEE
id = 133
iva = 15
ivd = 15
ivs = 15
lvl = 1

start0 = time.time()

# 1. Evos
print("\nGet Evolutons...")
names = []
start = time.time()
evos = get_evolutions_from_gamemaster(id,gm,pokemon_names)
end = time.time()

for x in evos:
    names.append(pokemon_names[str(x)])
print("This took: %s Seconds" % (end - start))
print("Evoltions: %s" % evos)
print("Names: %s" % names)

# 2. Base stats
print("\nGet Base stats...")
start = time.time()
base = []
for x in evos:
    base.append(get_stats_from_gamemaster(x,gm,pokemon_names))
end = time.time()
print("This took: %s Seconds" % (end - start))
print("Base stats: %s" % base)

# 3. Own Ranking
print("\nCalculate own ranking...")
start = time.time()
ranks = []
maxcp = []
for x in base:
    max_l, max_cp = get_maximum_level(id,x['pokemon_stats_a'],x['pokemon_stats_d'],x['pokemon_stats_s'],
                      iva,ivd,ivs,lvl,cp_multiplier)
    max_cpm = cp_multiplier[str(max_l)]
    maxcp.append(max_cp)
    rank_val = math.pow(max_cpm,2)*(x['pokemon_stats_a']+iva)*(x['pokemon_stats_d']+ivd)* \
                 math.floor(max_cpm*(x['pokemon_stats_s']+ivs))
    ranks.append(rank_val)
end = time.time()
print("This took: %s Seconds" % (end - start))
print("Maximum CP: %s" % maxcp)
print("Own ranking: %s" % ranks)

# 4. Find ranking in rank-file
print("\nFind overall ranking...")
start = time.time()
ranking = []
perfection = []
i = 0
for x in evos:
    ranklist = ranking_data['pkmn_%s' % x]
    ranking.append(ranklist.index(ranks[i])+1)
    perfection.append(100*(ranks[i]/ranklist[0]))
    i += 1
end = time.time()
print("This took: %s Seconds" % (end - start))
print("Overall ranking: %s" % ranking)
print("Perfection: %s%%" % perfection)

end0 = time.time()
print("\nALL took: %s Seconds" % (end0 - start0))

# Works clean and fast
