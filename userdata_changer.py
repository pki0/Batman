import json
import os

allids = os.listdir("userdata/")
newids = []

#to_add = ["user_pvp_buddy","user_pvp_league_1500","user_pvp_league_2500"]
#keys_to_add = ["user_pvp_max_level_40", "user_pvp_max_level_50"]
#values_to_add = [False, True]


for x in allids:
    filename = "userdata/" + x

    with open(filename, 'r', encoding='utf-8') as f:
        user_settings = json.loads(f.read())
    #for i in to_add:
        #user_settings[i] = False
    user_settings["user_pvp_max_level_40"] = False
    user_settings["user_pvp_max_level_50"] = True

    with open(filename, 'w') as fp:
        json.dump(user_settings, fp)

