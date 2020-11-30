import math


def get_maximum_level(base_attack, base_defense, base_stamina, iv_attack, iv_defense, iv_stamina, league_cp, cp_multiplier):
    for level in cp_multiplier:
        cp = calculate_cp(base_attack, base_defense, base_stamina, iv_attack, iv_defense, iv_stamina, cp_multiplier[str(level)])
        if cp > league_cp:
            level = float(level) - 0.5
            cp = calculate_cp(base_attack, base_defense, base_stamina, iv_attack, iv_defense, iv_stamina, cp_multiplier[str(level)])
            break

    return level


def calculate_cp(base_attack, base_defense, base_stamina, iv_attack, iv_defense, iv_stamina, cp_multiplier):

    return math.floor((base_attack + int(iv_attack)) * math.pow((base_defense + int(iv_defense)),0.5) * \
      math.pow((base_stamina + int(iv_stamina)),0.5) * math.pow(cp_multiplier,2)/10)


def calculate_rank(base_attack, base_defense, base_stamina, iv_attack, iv_defense, iv_stamina, max_cpm):

    return math.pow(max_cpm,2)*(base_attack+iv_attack)*(base_defense+iv_defense)*math.floor(max_cpm*(base_stamina+iv_stamina))


def get_pvp_values(base_attack, base_defense, base_stamina, iv_attack, iv_defense, iv_stamina, league_cp, cp_multiplier):
    pvp_level = get_maximum_level(base_attack, base_defense, base_stamina, iv_attack, iv_defense, iv_stamina, league_cp, cp_multiplier)
    pvp_cp = calculate_cp(base_attack, base_defense, base_stamina, iv_attack, iv_defense, iv_stamina, cp_multiplier[str(pvp_level)])
    pvp_rank = calculate_rank(base_attack, base_defense, base_stamina, iv_attack, iv_defense, iv_stamina, cp_multiplier[str(pvp_level)])

    return pvp_level, pvp_cp, pvp_rank
