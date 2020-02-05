import json
import os

allids = os.listdir("userdata/")
newids = []

to_add = ["user_pvp_max_league", "user_pvp_max_rank"]


for x in allids:
    filename = "userdata/" + x

    with open(filename, 'r', encoding='utf-8') as f:
        user_settings = json.loads(f.read())
    print(user_settings)
    for i in to_add:
        user_settings[i] = None
    print(user_settings)
    with open(filename, 'w') as fp:
        json.dump(user_settings, fp)

