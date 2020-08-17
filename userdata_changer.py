import json
import os

allids = os.listdir("userdata/")
newids = []

#to_add = ["user_pvp_buddy","user_pvp_league_1500","user_pvp_league_2500"]
to_add = ["user_pvp_max_rank"]

for x in allids:
    filename = "userdata/" + x

    with open(filename, 'r', encoding='utf-8') as f:
        user_settings = json.loads(f.read())
    #print(user_settings)
    for i in to_add:
        user_settings[i] = 100 #False
    #print(user_settings)
    with open(filename, 'w') as fp:
        json.dump(user_settings, fp)

