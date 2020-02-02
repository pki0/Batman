import math

def get_maximum_level(poke_id, base_a, base_d, base_s, iv_a, iv_d, iv_s, poke_level, cp_multiplier):
    for x in cp_multiplier:
        # WTF this continue is an extrem speeeeeeeeed up by factor 3-4 oO
        if float(x) < poke_level:
            continue
        cp = math.floor((base_a + int(iv_a)) * math.pow((base_d + int(iv_d)),0.5) * \
            math.pow((base_s + int(iv_s)),0.5) * math.pow(cp_multiplier[str(x)],2)/10)
        if cp > 1500:
            x = float(x) - 0.5
            cp = math.floor((base_a + int(iv_a)) * math.pow((base_d + int(iv_d)),0.5) * \
                math.pow((base_s + int(iv_s)),0.5) * math.pow(cp_multiplier[str(x)],2)/10)
            break
            # Fuck it... why is break so much faster then returning here?! *Middlefinger*
    return x, cp
