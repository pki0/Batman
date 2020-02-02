import math

def get_maximum_level(poke_id, base_a, base_d, base_s, iv_a, iv_d, iv_s, max_cp, cp_multiplier):
    for x in cp_multiplier:
        cp = math.floor((base_a + int(iv_a)) * math.pow((base_d + int(iv_d)),0.5) * \
            math.pow((base_s + int(iv_s)),0.5) * math.pow(cp_multiplier[str(x)],2)/10)
        if cp > max_cp:
            x = float(x) - 0.5
            cp = math.floor((base_a + int(iv_a)) * math.pow((base_d + int(iv_d)),0.5) * \
                math.pow((base_s + int(iv_s)),0.5) * math.pow(cp_multiplier[str(x)],2)/10)
            break
            # Fuck it... why is break so much faster then returning here?! *Middlefinger*
    return x, cp

def calculate_rank(base_a, base_d, base_s, iv_a, iv_d, iv_s, max_cpm):
    rank = math.pow(max_cpm,2)*(base_a+iv_a)*(base_d+iv_d)*math.floor(max_cpm*(base_s+iv_s))
    return rank
