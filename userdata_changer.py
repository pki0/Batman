import json
import os

allids = os.listdir("userdata/")
newids = []

input = '    "user_send_venue":1,\n    "user_attack_min":0,\n' + \
'    "user_attack_max":15,\n    "user_defense_min":0,\n' + \
'    "user_defense_max":15,\n    "user_stamina_min":0,\n' + \
'    "user_stamina_max":15,\n' + '}'


for x in allids:
    filename = "userdata/" + x

    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    last_line = lines[:-1]
    last_element = last_line[-1]
    mod_last_element = ''.join((last_element[:-1],',\n'))
    lines = lines[:-2]
    lines.append(mod_last_element)
    lines.append(input)

    f = open(filename, "w")
    for line in lines:
        #if line!= "}":
        f.write(line)
    f.close()