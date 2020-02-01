import json
import time
import math


gamemaster_file = 'gamemaster.json'
locale_file = 'locales/pokemon.de.json'

# Read GamemasterFile
try:
    with open(gamemaster_file, 'r', encoding='utf-8') as f:
        gamemaster_data = json.loads(f.read())

except Exception as e:
    logger.error('%s' % (repr(e)))
    # Pass to ignore if some files missing.
    pass
# Read locales for testing
try:
    with open(locale_file, 'r', encoding='utf-8') as f:
        pokemon_names = json.loads(f.read())
except Exception as e:
    logger.error('%s' % (repr(e)))
    # Pass to ignore if some files missing.
    pass


# Filter the GM to very few entries but special forms are now broken... give a shit on it?
new_gm = dict()
j = 1
for i in gamemaster_data["itemTemplates"]:
    if "V0" in i["templateId"] and \
       "COMBAT" not in i["templateId"] and \
       "MOVE" not in i["templateId"] and \
       "FORMS" not in i["templateId"] and \
       "SPAWN" not in i["templateId"] and \
       len(i["templateId"].split("_")) == 3:
        new_gm[j] = i
        j += 1



# Now get Evos: This function is fast enough xe-5 seconds...
def get_evolution_and_stats_from_gamemaster_by_pokemon_id(poke_id, new_gm, pokemon_names):
    # Check for prevolution
    i = 1
    evos = dict()
    evos[i] = {}
    evos[i]["pokemon_id"] = poke_id
    evos[i]["pokemon_name"] = pokemon_names[str(poke_id)]
    # Find baste stats once
    for x in new_gm.items():
        if str(poke_id).zfill(4) in x[1]['templateId'][1:5] and 'pokemonSettings' in x[1]:
            evos[i]["pokemon_stats_a"] = x[1]["pokemonSettings"]["stats"]["baseAttack"]
            evos[i]["pokemon_stats_d"] = x[1]["pokemonSettings"]["stats"]["baseDefense"]
            evos[i]["pokemon_stats_s"] = x[1]["pokemonSettings"]["stats"]["baseStamina"]
            break

    while "evolutionIds" in new_gm[poke_id]["pokemonSettings"] or "evolutionBranch" in new_gm[poke_id]["pokemonSettings"]:
        if "evolutionIds" in new_gm[poke_id]["pokemonSettings"]:
        # Now find the Evolution in GM
            for x in new_gm.items():
                if new_gm[poke_id]["pokemonSettings"]["evolutionIds"][0] == x[1]["pokemonSettings"]["pokemonId"]:
                    i += 1
                    evo_id = x[1]["templateId"]
                    evos[i] = {}
                    evos[i]["pokemon_id"] = int(evo_id[1:5])
                    evos[i]["pokemon_name"] = pokemon_names[str(int(evo_id[1:5]))]
                    evos[i]["pokemon_stats_a"] = x[1]["pokemonSettings"]["stats"]["baseAttack"]
                    evos[i]["pokemon_stats_d"] = x[1]["pokemonSettings"]["stats"]["baseDefense"]
                    evos[i]["pokemon_stats_s"] = x[1]["pokemonSettings"]["stats"]["baseStamina"]
                    poke_id = int(evo_id[1:5])
                    break
        # Special case for stone-evos
        elif "evolutionBranch" in new_gm[poke_id]["pokemonSettings"]:
            for x in new_gm.items():
                if new_gm[poke_id]["pokemonSettings"]["evolutionBranch"][0]["evolution"] == x[1]["pokemonSettings"]["pokemonId"]:
                    i += 1
                    evo_id = x[1]["templateId"]
                    evos[i] = {}
                    evos[i]["pokemon_id"] = int(evo_id[1:5])
                    evos[i]["pokemon_name"] = pokemon_names[str(int(evo_id[1:5]))]
                    evos[i]["pokemon_stats_a"] = x[1]["pokemonSettings"]["stats"]["baseAttack"]
                    evos[i]["pokemon_stats_d"] = x[1]["pokemonSettings"]["stats"]["baseDefense"]
                    evos[i]["pokemon_stats_s"] = x[1]["pokemonSettings"]["stats"]["baseStamina"]
                    poke_id = int(evo_id[1:5])
                    break
    return evos

# TESTING
'''
start = time.time()

evo = get_evolution_and_stats_from_gamemaster_by_pokemon_id(1,new_gm,pokemon_names)

end = time.time()
print("This took: %s Seconds" % (end - start))
print(evo)

start = time.time()
evo = get_evolution_and_stats_from_gamemaster_by_pokemon_id(111,new_gm,pokemon_names)

end = time.time()
print("This took: %s Seconds" % (end - start))
print(evo)
'''

# Function for pvp

CPMultiplier = {
     '1.0':0.094,        '1.5':0.1351374318,
     '2.0':0.16639787,   '2.5':0.192650919,
     '3.0':0.21573247,   '3.5':0.2365726613,
     '4.0':0.25572005,   '4.5':0.2735303812,
     '5.0':0.29024988,   '5.5':0.3060573775,
     '6.0':0.3210876,    '6.5':0.3354450362,
     '7.0':0.34921268,   '7.5':0.3624577511,
     '8.0':0.37523559,   '8.5':0.387592416,
     '9.0':0.39956728,   '9.5':0.4111935514,
    '10.0':0.42250001,  '10.5':0.4329264091,
    '11.0':0.44310755,  '11.5':0.4530599591,
    '12.0':0.46279839,  '12.5':0.472336093,
    '13.0':0.48168495,  '13.5':0.4908558003,
    '14.0':0.49985844,  '14.5':0.508701765,
    '15.0':0.51739395,  '15.5':0.5259425113,
    '16.0':0.53435433,  '16.5':0.5426357375,
    '17.0':0.55079269,  '17.5':0.5588305862,
    '18.0':0.56675452,  '18.5':0.5745691333,
    '19.0':0.58227891,  '19.5':0.5898879072,
    '20.0':0.59740001,  '20.5':0.6048236651,
    '21.0':0.61215729,  '21.5':0.6194041216,
    '22.0':0.62656713,  '22.5':0.6336491432,
    '23.0':0.64065295,  '23.5':0.6475809666,
    '24.0':0.65443563,  '24.5':0.6612192524,
    '25.0':0.667934,    '25.5':0.6745818959,
    '26.0':0.68116492,  '26.5':0.6876849038,
    '27.0':0.69414365,  '27.5':0.70054287,
    '28.0':0.70688421,  '28.5':0.7131691091,
    '29.0':0.71939909,  '29.5':0.7255756136,
    '30.0':0.7317,      '30.5':0.7347410093,
    '31.0':0.73776948,  '31.5':0.7407855938,
    '32.0':0.74378943,  '32.5':0.7467812109,
    '33.0':0.74976104,  '33.5':0.7527290867,
    '34.0':0.75568551,  '34.5':0.7586303683,
    '35.0':0.76156384,  '35.5':0.7644860647,
    '36.0':0.76739717,  '36.5':0.7702972656,
    '37.0':0.7731865,   '37.5':0.7760649616,
    '38.0':0.77893275,  '38.5':0.7817900548,
    '39.0':0.78463697,  '39.5':0.7874736075,
    '40.0':0.79030001,  '40.5':0.792803946731,
    '41.0':0.7928039467,'41.5':0.797803921997,
    '42.0':0.8003,      '42.5':0.802803892616,
    '43.0':0.8053,      '43.5':0.807803863507,
    '44.0':0.81029999,  '44.5':0.812803834725,
    '45.0':0.81529999
  }





def pvpivcalc(poke_id, new_gm, pokemon_names, iv_a, iv_d, iv_s, poke_level, CPMultiplier):
    # Get the data
    evo = get_evolution_and_stats_from_gamemaster_by_pokemon_id(poke_id,new_gm,pokemon_names)
    print(evo)
    # Get Base stats
    iv_base_a = int(evo[1]["pokemon_stats_a"])
    iv_base_d = int(evo[1]["pokemon_stats_d"])
    iv_base_s = int(evo[1]["pokemon_stats_s"])
    ## Now calculate all possible IV combos

    # First calc the maximum level for CP < 1500
    max_level_p, max_cp_p  = get_maximum_level(poke_id, iv_base_a, iv_base_d, iv_base_s, iv_a, iv_d, iv_s, 0, CPMultiplier)
    k = 1
    # Shit on comments from here... :D
    score_dict = dict()
    for iv0_a in range(0,16):
        for iv0_d in range(0,16):
            for iv0_s in range(0,16):
                max_level, cp_tmp  = get_maximum_level(poke_id, iv_base_a, iv_base_d, iv_base_s, iv0_a, iv0_d, iv0_s, float(max_level_p)-2, CPMultiplier)
                max_cpm  = CPMultiplier[str(max_level)]
                rank_val = math.pow(max_cpm,2)*(iv_base_a+iv0_a)*(iv_base_d+iv0_d)*math.floor(max_cpm*(iv_base_s+iv0_s))
                score_dict[k] = {"score":rank_val, "iv0_a":iv0_a, "iv0_d":iv0_d, "iv0_s":iv0_s}
                k += 1

    rank_needed = 0
    i = 0
    for key in score_dict:
        if score_dict[key]["iv0_a"] == iv_a and score_dict[key]["iv0_d"] == iv_d and score_dict[key]["iv0_s"] == iv_s:
            rank_needed = score_dict[key]["score"]
            break
    # Some sort form Stackoverflow
    sorted_score = sorted(score_dict.items(), key=lambda item: int(item[1]['score']))

    for key in sorted_score:
        if key[1]["score"] == rank_needed:
            # is this also slow? return len(sorted_score)-i, max_level_p, max_cp_p
            break
        i += 1

    return len(sorted_score)-i, max_level_p, max_cp_p


def get_maximum_level(poke_id, iv_base_a, iv_base_d, iv_base_s, iv_a, iv_d, iv_s, poke_level, CPMultiplier):
    for x in CPMultiplier:
        # WTF this continue is an extrem speeeeeeeeed up by factor 3-4 oO
        if float(x) < poke_level:
            continue
        cp = math.floor((iv_base_a + int(iv_a)) * math.pow((iv_base_d + int(iv_d)),0.5) * \
            math.pow((iv_base_s + int(iv_s)),0.5) * math.pow(CPMultiplier[str(x)],2)/10)
        if cp > 1500:
            x = float(x) - 0.5
            cp = math.floor((iv_base_a + int(iv_a)) * math.pow((iv_base_d + int(iv_d)),0.5) * \
                math.pow((iv_base_s + int(iv_s)),0.5) * math.pow(CPMultiplier[str(x)],2)/10)
            break
            # Fuck it... why is break so much faster then returning here?! *Middlefinger*
    return x, cp


# TESTING

start = time.time()
rank, level, cp = pvpivcalc(334,new_gm,pokemon_names,0,14,15,10,CPMultiplier)
end = time.time()
print("This took: %s Seconds" % (end - start))
print("%s (0,14,15))-> Rang %s -> Level %s -> WP %s" % (pokemon_names["334"],rank,level,cp))

start = time.time()
rank, level, cp = pvpivcalc(334,new_gm,pokemon_names,0,15,14,10,CPMultiplier)
end = time.time()
print("This took: %s Seconds" % (end - start))
print("%s (0,15,14))-> Rang %s -> Level %s -> WP %s" % (pokemon_names["334"],rank,level,cp))

start = time.time()
rank, level, cp = pvpivcalc(379,new_gm,pokemon_names,10,10,10,10,CPMultiplier)
end = time.time()
print("This took: %s Seconds" % (end - start))
print("%s (10,10,10))-> Rang %s -> Level %s -> WP %s" % (pokemon_names["379"],rank,level,cp))


