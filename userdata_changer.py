import json
import os

allids = os.listdir("userdata/")
newids = []


last_line = '    "user_send_venue":1\n'

input = '    "user_send_venue":1,\n    "user_attack_min":0,\n' + \
'    "user_attack_max":15,\n    "user_defense_min":0,\n' + \
'    "user_defense_max":15,\n    "user_stamina_min":0,\n' + \
'    "user_stamina_max":15,\n' + '}\n'


for x in allids:
    filename = "userdata/" + x



    #filename = "data.json"


    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    f = open(filename, "w")
    for line in lines:
        if line!= "}"+"\n":
            f.write(line)
    f.close()

    f = open(filename, "r")
    lines = f.readlines()
    f.close()

    f = open(filename, "w")
    for line in lines:
        if line!= last_line:
            f.write(line)
    f.close()


    with open(filename, 'a') as file:
        file.write(input)
        file.close()
