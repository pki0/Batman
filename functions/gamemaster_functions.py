def cut_gamemaster(gamemaster_data):
    # Filter the GameMaster to very few entries but special forms are now broken... give a shit on it?
    new_gm = dict()
    j = 1
    for i in gamemaster_data["itemTemplates"]:
        if ("V0" in i["templateId"] and \
           "COMBAT" not in i["templateId"] and \
           "MOVE" not in i["templateId"] and \
           "FORMS" not in i["templateId"] and \
           "SPAWN" not in i["templateId"] and \
           len(i["templateId"].split("_")) == 3) or \
           (len(i["templateId"].split("_")) == 4 and (i["templateId"].split("_"))[2] in ("HO", "MR", "MIME",  "PORYGON")):

            new_gm[j] = i
            j += 1

    return new_gm


def get_evolutions_from_gamemaster(pokemon_id,gamemaster_data,pokemon_names):
    # Cancel if poke_id is not available
    if str(pokemon_id) not in pokemon_names:
        return None

    evolutions = list()
    evolutions.append(pokemon_id)
    i = 1
    found = False
    # Find in GamemasterFile
    for x in gamemaster_data.items():
        if str(pokemon_id).zfill(4) in x[1]['templateId'][1:5] and 'pokemonSettings' in x[1]:
            found = True
            break
    # Not found
    if found == False:
        return None

    while "evolutionBranch" in x[1]["pokemonSettings"]:
        found = False
        if "evolutionBranch" in x[1]["pokemonSettings"]:
            if "evolution" in x[1]["pokemonSettings"]["evolutionBranch"][0]:
                if len(x[1]["pokemonSettings"]["evolutionBranch"]) == 1:
                    # Special case for loop evos. Fuck you Nia
                    if "parentPokemonId" in x[1]["pokemonSettings"] and (x[1]["pokemonSettings"]["parentPokemonId"] == x[1]["pokemonSettings"]["evolutionBranch"][0]["evolution"]):
                        return evolutions
                    for y in gamemaster_data.items():
                        if x[1]["pokemonSettings"]["evolutionBranch"][0]["evolution"] == y[1]["pokemonSettings"]["pokemonId"]:
                            i += 1
                            evo_poke_id = int(y[1]["templateId"][1:5])
                            evolutions.append(evo_poke_id)
                            x = y
                            found = True
                            break
                    # If not found => return
                    if found == False:
                        return evolutions
                elif len(x[1]["pokemonSettings"]["evolutionBranch"]) > 1:
                    for z in x[1]["pokemonSettings"]["evolutionBranch"]:
                        if "evolution" not in z:
                            return evos # break while
                        for y in gamemaster_data.items():
                            if z["evolution"] == y[1]["pokemonSettings"]["pokemonId"]:
                                i += 1
                                evo_poke_id = int(y[1]["templateId"][1:5])
                                evolutions.append(evo_poke_id)
                                break
                    return evolutions # break while if all are done
            # Sepcial case if evolutionBranch is available but no evolution entry
            else:
                return evolutions
    return evolutions


def get_stats_from_gamemaster(pokemon_id,gamemaster_data,pokemon_names):
    # Cancel if poke_id is not available
    if str(pokemon_id) not in pokemon_names:
        return None

    found = False
    stats = dict()

    # Find baste stats once
    for x in gamemaster_data.items():
        if str(pokemon_id).zfill(4) in x[1]['templateId'][1:5] and 'pokemonSettings' in x[1]:
            stats["baseAttack"] = x[1]["pokemonSettings"]["stats"]["baseAttack"]
            stats["baseDefense"] = x[1]["pokemonSettings"]["stats"]["baseDefense"]
            stats["baseStamina"] = x[1]["pokemonSettings"]["stats"]["baseStamina"]
            found = True
            return stats
    # Finished but not found...
    if found == False:
        return None
